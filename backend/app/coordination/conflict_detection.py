import uuid
from typing import List, Dict, Set
from app.models.agent import AgentPosition, PositionType
from app.models.state import SharedBusinessState, Conflict, ConflictType, ConflictStatus, StateStatus


class ConflictDetectionAgent:
    """
    Conflict Detection Coordination Agent.
    Analyzes agent positions returned by specialist agents, identifies disagreements,
    categorizes conflict types, assigns severity, and updates SharedBusinessState.
    """

    def detect_conflicts(
        self, state: SharedBusinessState, positions: List[AgentPosition]
    ) -> List[Conflict]:
        """
        Executes deterministic conflict detection rules across a collection of AgentPosition outputs.
        Populates state.conflicts and updates state.status accordingly.
        """
        conflicts: List[Conflict] = []

        if not positions or len(positions) < 2:
            # Need at least 2 positions to compare for conflict
            return conflicts

        # 1. Position Conflicts (Stance Divergence)
        conflicts.extend(self._detect_position_conflicts(positions))

        # 2. Assumption Conflicts (Incompatible Premises)
        conflicts.extend(self._detect_assumption_conflicts(positions))

        # 3. Constraint Conflicts (Constraint Violations / Incompatibilities)
        conflicts.extend(self._detect_constraint_conflicts(state, positions))

        # 4. Evidence Conflicts (Contradictory Claims & Evidence)
        conflicts.extend(self._detect_evidence_conflicts(positions))

        # Update SharedBusinessState
        state.conflicts = conflicts
        if conflicts:
            state.status = StateStatus.CONFLICT_DETECTED

        return conflicts

    def _detect_position_conflicts(self, positions: List[AgentPosition]) -> List[Conflict]:
        conflicts = []
        n = len(positions)
        for i in range(n):
            for j in range(i + 1, n):
                p1, p2 = positions[i], positions[j]
                pos1, pos2 = p1.position, p2.position

                # Direct Opposite Position Conflict: RECOMMEND vs DO_NOT_RECOMMEND
                if (pos1 == PositionType.RECOMMEND and pos2 == PositionType.DO_NOT_RECOMMEND) or (
                    pos1 == PositionType.DO_NOT_RECOMMEND and pos2 == PositionType.RECOMMEND
                ):
                    conflicts.append(
                        Conflict(
                            conflict_id=f"cnf-{uuid.uuid4().hex[:12]}",
                            agents_involved=[p1.agent_name, p2.agent_name],
                            conflict_type=ConflictType.POSITION_CONFLICT,
                            description=f"Direct strategic recommendation contradiction: '{p1.agent_name}' advocates {pos1.value.upper()} while '{p2.agent_name}' advocates {pos2.value.upper()}.",
                            conflicting_claims=[
                                f"{p1.agent_name} position: {pos1.value}",
                                f"{p2.agent_name} position: {pos2.value}",
                            ],
                            conflicting_assumptions=list(set(p1.assumptions + p2.assumptions)),
                            severity="high",
                            status=ConflictStatus.OPEN,
                            supporting_evidence=p1.evidence + p2.evidence,
                        )
                    )

                # Partial Position Conflict: RECOMMEND vs CONDITIONAL or DO_NOT_RECOMMEND vs CONDITIONAL
                elif (pos1 == PositionType.RECOMMEND and pos2 == PositionType.CONDITIONAL) or (
                    pos1 == PositionType.CONDITIONAL and pos2 == PositionType.RECOMMEND
                ) or (pos1 == PositionType.DO_NOT_RECOMMEND and pos2 == PositionType.CONDITIONAL) or (
                    pos1 == PositionType.CONDITIONAL and pos2 == PositionType.DO_NOT_RECOMMEND
                ):
                    conflicts.append(
                        Conflict(
                            conflict_id=f"cnf-{uuid.uuid4().hex[:12]}",
                            agents_involved=[p1.agent_name, p2.agent_name],
                            conflict_type=ConflictType.POSITION_CONFLICT,
                            description=f"Partial strategic recommendation variance: '{p1.agent_name}' is {pos1.value.upper()} while '{p2.agent_name}' is {pos2.value.upper()}.",
                            conflicting_claims=[
                                f"{p1.agent_name} stance: {pos1.value}",
                                f"{p2.agent_name} stance: {pos2.value}",
                            ],
                            conflicting_assumptions=list(set(p1.assumptions + p2.assumptions)),
                            severity="medium",
                            status=ConflictStatus.OPEN,
                            supporting_evidence=p1.evidence + p2.evidence,
                        )
                    )
        return conflicts

    def _detect_assumption_conflicts(self, positions: List[AgentPosition]) -> List[Conflict]:
        conflicts = []
        n = len(positions)
        
        # Opposing concept pairs for assumption keyword comparison
        opposing_pairs = [
            ("sufficient", "insufficient"),
            ("adequate", "inadequate"),
            ("high", "low"),
            ("feasible", "unfeasible"),
            ("viable", "unviable"),
            ("profitable", "unprofitable"),
        ]

        for i in range(n):
            for j in range(i + 1, n):
                p1, p2 = positions[i], positions[j]
                p1_assumptions = p1.assumptions
                p2_assumptions = p2.assumptions

                conflicting_pairs = []
                for a1 in p1_assumptions:
                    for a2 in p2_assumptions:
                        a1_lower, a2_lower = a1.lower(), a2.lower()
                        for word1, word2 in opposing_pairs:
                            if (word1 in a1_lower and word2 in a2_lower) or (word2 in a1_lower and word1 in a2_lower):
                                conflicting_pairs.append((a1, a2))

                if conflicting_pairs:
                    conflicts.append(
                        Conflict(
                            conflict_id=f"cnf-{uuid.uuid4().hex[:12]}",
                            agents_involved=[p1.agent_name, p2.agent_name],
                            conflict_type=ConflictType.ASSUMPTION_CONFLICT,
                            description=f"Contradictory assumptions identified between '{p1.agent_name}' and '{p2.agent_name}'.",
                            conflicting_claims=[
                                f"{p1.agent_name} assumption: '{c[0]}'" for c in conflicting_pairs
                            ],
                            conflicting_assumptions=[c[0] for c in conflicting_pairs] + [c[1] for c in conflicting_pairs],
                            severity="medium",
                            status=ConflictStatus.OPEN,
                            supporting_evidence=p1.evidence + p2.evidence,
                        )
                    )
        return conflicts

    def _detect_constraint_conflicts(
        self, state: SharedBusinessState, positions: List[AgentPosition]
    ) -> List[Conflict]:
        conflicts = []
        canonical_constraints = [c.lower() for c in state.constraints]

        for p in positions:
            p_constraints = [c.lower() for c in p.constraints_assumed]
            
            # Check if an agent assumes a constraint that contradicts a canonical constraint
            for c_canon in canonical_constraints:
                for c_agent in p_constraints:
                    if ("limit" in c_canon and "exceed" in c_agent) or ("max" in c_canon and "beyond" in c_agent):
                        conflicts.append(
                            Conflict(
                                conflict_id=f"cnf-{uuid.uuid4().hex[:12]}",
                                agents_involved=[p.agent_name, "Canonical Business State"],
                                conflict_type=ConflictType.CONSTRAINT_CONFLICT,
                                description=f"Agent '{p.agent_name}' assumed constraint '{c_agent}' conflicts with canonical constraint '{c_canon}'.",
                                conflicting_claims=[
                                    f"Canonical state constraint: {c_canon}",
                                    f"Agent {p.agent_name} constraint assumed: {c_agent}",
                                ],
                                conflicting_assumptions=p.assumptions,
                                severity="high",
                                status=ConflictStatus.OPEN,
                                supporting_evidence=p.evidence,
                            )
                        )
        return conflicts

    def _detect_evidence_conflicts(self, positions: List[AgentPosition]) -> List[Conflict]:
        conflicts = []
        n = len(positions)

        for i in range(n):
            for j in range(i + 1, n):
                p1, p2 = positions[i], positions[j]
                claims1 = [c.claim.lower() for c in p1.key_claims]
                claims2 = [c.claim.lower() for c in p2.key_claims]

                opposing_claims = []
                for c1_raw, c1_lower in zip(p1.key_claims, claims1):
                    for c2_raw, c2_lower in zip(p2.key_claims, claims2):
                        # Detect opposing evidence keywords in claims
                        if ("validated" in c1_lower and "missing" in c2_lower and "demand" in c1_lower and "demand" in c2_lower) or \
                           ("high" in c1_lower and "low" in c2_lower and "margin" in c1_lower and "margin" in c2_lower):
                            opposing_claims.append((c1_raw.claim, c2_raw.claim))

                if opposing_claims:
                    conflicts.append(
                        Conflict(
                            conflict_id=f"cnf-{uuid.uuid4().hex[:12]}",
                            agents_involved=[p1.agent_name, p2.agent_name],
                            conflict_type=ConflictType.EVIDENCE_CONFLICT,
                            description=f"Contradictory evidence claims between '{p1.agent_name}' and '{p2.agent_name}'.",
                            conflicting_claims=[f"Claim A: {pair[0]}" for pair in opposing_claims] + [f"Claim B: {pair[1]}" for pair in opposing_claims],
                            conflicting_assumptions=[],
                            severity="low",
                            status=ConflictStatus.OPEN,
                            supporting_evidence=p1.evidence + p2.evidence,
                        )
                    )
        return conflicts
