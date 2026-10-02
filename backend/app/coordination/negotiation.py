from typing import List, Tuple, Dict, Any, Optional
from app.models.agent import AgentPosition, PositionType
from app.models.state import (
    SharedBusinessState,
    Conflict,
    ConflictStatus,
    ConflictType,
    NegotiationRound,
    StateStatus,
)


class NegotiationAgent:
    """
    Agent-to-Agent Negotiation Coordination Layer.
    Facilitates structured evidence exchange and position reconsideration between conflicting specialist agents.
    Supports justified position revisions while preserving minority dissent when agreement is not justified.
    """

    def run_negotiation(
        self,
        state: SharedBusinessState,
        positions: List[AgentPosition],
        conflicts: List[Conflict],
    ) -> Tuple[SharedBusinessState, List[NegotiationRound]]:
        """
        Processes open conflicts through deterministic negotiation protocol rounds.
        Updates state.negotiation_history, state.revised_positions, conflict statuses, and state.status.
        Preserves immutability of state.agent_positions and maintains strict round-by-round position consistency.
        """
        rounds: List[NegotiationRound] = []
        open_conflicts = [c for c in conflicts if c.status == ConflictStatus.OPEN]

        if not open_conflicts:
            # No open conflicts to negotiate; revised positions match incoming positions preserving ordering
            state.revised_positions = [p.model_copy(deep=True) for p in positions]
            return state, rounds

        # Track the evolving positions state across rounds, initialized from incoming positions
        current_positions: Dict[str, AgentPosition] = {
            p.agent_name: p.model_copy(deep=True) for p in positions
        }

        state.status = StateStatus.NEGOTIATING

        round_counter = len(state.negotiation_history) + 1

        for conflict in open_conflicts:
            participants = conflict.agents_involved
            # Get the exact snapshot of participating agents at the start of THIS round
            round_start_positions = [
                current_positions[name].model_copy(deep=True)
                for name in participants
                if name in current_positions
            ]

            if len(round_start_positions) < 2:
                # Need at least 2 active specialist positions
                continue

            # STEP A: Capture positions at the start of this round
            prev_positions = [p.model_copy(deep=True) for p in round_start_positions]

            # STEP B: Exchange Evidence & Build Arguments based on round-start stances
            evidence_exchanged: List[str] = []
            arguments: List[str] = []

            for p in round_start_positions:
                ev_str = (
                    f"{p.agent_name} presented evidence: "
                    f"{', '.join(p.evidence[:2]) if p.evidence else 'No explicit evidence provided.'}"
                )
                evidence_exchanged.append(ev_str)

                arg_str = (
                    f"{p.agent_name} stance is {p.position.value.upper()} based on assumptions: "
                    f"{', '.join(p.assumptions[:2]) if p.assumptions else 'Default domain stance.'}"
                )
                arguments.append(arg_str)

            # Check if positions for these participants were already reconciled by an earlier round's revision
            pos_types = {p.position for p in round_start_positions}
            if len(pos_types) == 1 and conflict.conflict_type == ConflictType.POSITION_CONFLICT:
                # Positions are already aligned at the start of this round
                common_pos = next(iter(pos_types)).value.upper()
                is_resolvable = True
                resolution_msg = (
                    f"Conflict on '{conflict.description}' reconciled following prior position "
                    f"revisions to {common_pos}."
                )
                updated_positions = [p.model_copy(deep=True) for p in round_start_positions]
            else:
                # STEP C: Evaluate Revision Rules vs Dissent using positions at the start of this round
                is_resolvable, resolution_msg, updated_positions = self._evaluate_conflict_resolution(
                    conflict, round_start_positions
                )

            if is_resolvable:
                conflict.status = ConflictStatus.RESOLVED
                conflict.resolution = resolution_msg
                unresolved_points = []

                # Apply revised positions to the running state for subsequent rounds
                for updated in updated_positions:
                    current_positions[updated.agent_name] = updated.model_copy(deep=True)

            else:
                conflict.status = ConflictStatus.UNRESOLVED
                conflict.resolution = None
                unresolved_points = [
                    f"Unresolved stance discrepancy on issue '{conflict.description}': "
                    f"{round_start_positions[0].agent_name} ({round_start_positions[0].position.value}) vs "
                    f"{round_start_positions[1].agent_name} ({round_start_positions[1].position.value})."
                ]

            round_record = NegotiationRound(
                round_number=round_counter,
                participants=participants,
                issue=conflict.description,
                previous_positions=prev_positions,
                evidence_exchanged=evidence_exchanged,
                arguments=arguments,
                revised_positions=[
                    current_positions[name].model_copy(deep=True)
                    for name in participants
                    if name in current_positions
                ],
                resolution=resolution_msg if is_resolvable else None,
                unresolved_points=unresolved_points,
            )

            rounds.append(round_record)
            state.negotiation_history.append(round_record)
            round_counter += 1

        # Store final revised positions in SharedBusinessState preserving original specialist ordering
        state.revised_positions = [
            current_positions[p.agent_name].model_copy(deep=True)
            for p in positions
            if p.agent_name in current_positions
        ]

        # Check overall state status post-negotiation
        all_resolved = all(c.status == ConflictStatus.RESOLVED for c in conflicts)
        if all_resolved:
            state.status = StateStatus.CONSENSUS_REACHED
        else:
            state.status = StateStatus.NEGOTIATING

        return state, rounds

    def _evaluate_conflict_resolution(
        self, conflict: Conflict, agents: List[AgentPosition]
    ) -> Tuple[bool, Optional[str], List[AgentPosition]]:
        """
        Applies deterministic evidence-based revision rules.
        Returns (is_resolvable, resolution_summary, updated_agent_positions).
        """
        p1, p2 = agents[0], agents[1]
        pos1, pos2 = p1.position, p2.position

        # Rule 1: Financial DO_NOT_RECOMMEND vs Operations / Market CONDITIONAL or RECOMMEND
        # Resolvable if Operations/Market provides evidence of phased rollout / scope reduction that mitigates budget constraint
        if conflict.conflict_type == ConflictType.POSITION_CONFLICT:
            if (pos1 == PositionType.DO_NOT_RECOMMEND and pos2 in [PositionType.RECOMMEND, PositionType.CONDITIONAL]) or (
                pos2 == PositionType.DO_NOT_RECOMMEND and pos1 in [PositionType.RECOMMEND, PositionType.CONDITIONAL]
            ):
                strict_agent = p1 if pos1 == PositionType.DO_NOT_RECOMMEND else p2
                flex_agent = p2 if pos1 == PositionType.DO_NOT_RECOMMEND else p1

                # Check if evidence/assumptions mention scope, phasing, or pilot testing
                combined_text = " ".join(flex_agent.evidence + flex_agent.assumptions + flex_agent.recommended_actions).lower()

                if "pilot" in combined_text or "phase" in combined_text or "interview" in combined_text or "step" in combined_text or "15" in combined_text or "cap" in combined_text:
                    # Justified Revision: DO_NOT_RECOMMEND -> CONDITIONAL
                    revised_strict = strict_agent.model_copy(deep=True)
                    revised_strict.position = PositionType.CONDITIONAL
                    revised_strict.confidence = max(0.65, strict_agent.confidence - 0.10)
                    revised_strict.assumptions.append(
                        f"Position revised from DO_NOT_RECOMMEND to CONDITIONAL following {flex_agent.agent_name} evidence on phased rollout / pilot validation."
                    )
                    revised_strict.recommended_actions.append(
                        f"Cap initial capital deployment to pilot stage as proposed by {flex_agent.agent_name}."
                    )

                    revised_flex = flex_agent.model_copy(deep=True)
                    revised_flex.position = PositionType.CONDITIONAL
                    revised_flex.assumptions.append(
                        f"Adopted conditional stance incorporating {strict_agent.agent_name} capital constraint risk."
                    )

                    resolution_summary = (
                        f"{strict_agent.agent_name} revised position from DO_NOT_RECOMMEND to CONDITIONAL after "
                        f"{flex_agent.agent_name} introduced evidence for phased pilot rollout, satisfying budget constraints."
                    )
                    return True, resolution_summary, [revised_strict, revised_flex]

        # Rule 2: Assumption Conflict Resolution
        if conflict.conflict_type == ConflictType.ASSUMPTION_CONFLICT:
            # If assumptions clash on budget/capacity sufficiency, revise strict agent to CONDITIONAL upon pilot condition
            revised_agents = []
            for agent in [p1, p2]:
                r = agent.model_copy(deep=True)
                if r.position == PositionType.RECOMMEND:
                    r.position = PositionType.CONDITIONAL
                    r.assumptions.append("Conditioned stance on explicit assumption verification during pilot phase.")
                revised_agents.append(r)

            resolution_summary = (
                f"Assumption conflict between {p1.agent_name} and {p2.agent_name} reconciled by conditioning both stances "
                "on empirical pilot testing verification."
            )
            return True, resolution_summary, revised_agents

        # Rule 3: Unresolved Conflict (Dissent Preservation)
        # When neither agent's evidence invalidates the core concern, preserve original positions & dissent
        return False, None, [p1.model_copy(deep=True), p2.model_copy(deep=True)]
