"""
OrchestratorAgent — LangGraph State Machine Orchestrator
=========================================================
Wires the full multi-agent coordination pipeline as an explicit LangGraph
StateGraph. Each node corresponds to a distinct workflow stage. Conditional
edges implement branching based on structural state data (conflict presence,
severity, resolution status). No LLM calls, no external APIs, no majority voting.

Pipeline:
  START
    → initialize_state
    → run_specialists
    → detect_conflicts
    → [conditional] no_conflicts → synthesize
                    has_conflicts → negotiate
    → recheck_conflicts
    → [conditional] resolved/minor → synthesize
                    significant_unresolved → mark_human_review → synthesize
    → END
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from app.models.business import BusinessContext
from app.models.agent import AgentPosition, PositionType, AgentExecutionRecord
from app.models.state import (
    SharedBusinessState,
    Conflict,
    ConflictStatus,
    StateStatus,
    FinalDecision,
)
from app.agents import (
    MarketResearchAgent,
    FinancialAgent,
    CompetitionAgent,
    CustomerAgent,
    MarketingGTMAgent,
    OperationsAgent,
    RiskRegulatoryAgent,
)
from app.coordination.shared_goal import SharedGoalConsistencyAgent
from app.coordination.conflict_detection import ConflictDetectionAgent
from app.coordination.negotiation import NegotiationAgent


# ---------------------------------------------------------------------------
# Helper: Significant Conflict Predicate
# ---------------------------------------------------------------------------

def _is_significant_unresolved(conflict: Conflict) -> bool:
    """
    A conflict is 'significant' if it is unresolved AND has high or critical severity.
    These materially affect the final synthesis and may require human review.
    """
    return (
        conflict.status == ConflictStatus.UNRESOLVED
        and conflict.severity in ("high", "critical")
    )


# ---------------------------------------------------------------------------
# Node Implementations
# ---------------------------------------------------------------------------

def node_initialize_state(state: SharedBusinessState) -> SharedBusinessState:
    """
    Node: initialize_state
    Produces a canonical SharedBusinessState from the embedded BusinessContext.
    The business_context field is already populated; this node calls
    SharedGoalConsistencyAgent to derive canonical facts, constraints,
    assumptions, and open questions.
    """
    agent = SharedGoalConsistencyAgent()
    # initialize_state produces a fresh state from context; we use the
    # run_id already set (since the state was bootstrapped externally),
    # but replace all derived fields by calling agent logic directly.
    new_state = agent.initialize_state(state.business_context)
    # Preserve the run_id that was set during graph invocation
    new_state.run_id = state.run_id
    return new_state


def node_run_specialists(state: SharedBusinessState) -> SharedBusinessState:
    """
    Node: run_specialists
    Runs all 7 specialist agents with per-agent try/except isolation.
    Original positions are stored in state.agent_positions (never overwritten).
    Failures are recorded in state.execution_log without fabricating positions.
    """
    from app.agents.base import AgentExecutionContext

    agents = [
        MarketResearchAgent(),
        FinancialAgent(),
        CompetitionAgent(),
        CustomerAgent(),
        MarketingGTMAgent(),
        OperationsAgent(),
        RiskRegulatoryAgent(),
    ]

    execution_ctx = AgentExecutionContext(
        business_context=state.business_context,
        canonical_facts=list(state.canonical_facts),
        constraints=list(state.constraints),
        assumptions=list(state.assumptions),
    )

    positions: List[AgentPosition] = []
    log: List[AgentExecutionRecord] = []

    for agent in agents:
        try:
            position = agent.analyze(execution_ctx)
            positions.append(position)
            log.append(
                AgentExecutionRecord(
                    agent_name=agent.agent_name,
                    success=True,
                    position=position,
                )
            )
        except Exception as exc:  # noqa: BLE001
            log.append(
                AgentExecutionRecord(
                    agent_name=agent.agent_name,
                    success=False,
                    error=str(exc),
                )
            )

    state.agent_positions = positions  # originals — never overwritten after this
    state.execution_log = log
    state.status = StateStatus.ANALYZING
    return state


def node_detect_conflicts(state: SharedBusinessState) -> SharedBusinessState:
    """
    Node: detect_conflicts (first pass)
    Runs ConflictDetectionAgent on the original agent_positions.
    Updates state.conflicts and state.status.
    """
    if len(state.agent_positions) < 2:
        # Not enough positions to compare; skip detection
        return state

    agent = ConflictDetectionAgent()
    agent.detect_conflicts(state, state.agent_positions)
    return state


def node_negotiate(state: SharedBusinessState) -> SharedBusinessState:
    """
    Node: negotiate
    Runs NegotiationAgent on open conflicts.
    Results are stored in state.revised_positions and state.negotiation_history.
    Original state.agent_positions are NOT modified.
    """
    open_conflicts = [c for c in state.conflicts if c.status == ConflictStatus.OPEN]
    if not open_conflicts:
        return state

    agent = NegotiationAgent()
    updated_state, _ = agent.run_negotiation(
        state, list(state.agent_positions), open_conflicts
    )
    # NegotiationAgent writes to state.revised_positions and state.negotiation_history
    return updated_state


def node_recheck_conflicts(state: SharedBusinessState) -> SharedBusinessState:
    """
    Node: recheck_conflicts (second pass)
    Runs ConflictDetectionAgent on revised_positions (post-negotiation).
    Updates state.conflicts with any remaining disagreements.
    This explicitly verifies whether negotiation succeeded — we do not assume it did.
    """
    effective_positions = state.revised_positions if state.revised_positions else state.agent_positions
    if len(effective_positions) < 2:
        return state

    agent = ConflictDetectionAgent()
    # Run detection on revised positions; this appends to (or replaces) state.conflicts
    recheck_conflicts = agent.detect_conflicts(state, effective_positions)

    # Mark any conflict that was previously resolved as resolved in the new list
    resolved_ids = {
        c.conflict_id
        for c in state.conflicts
        if c.status == ConflictStatus.RESOLVED
    }
    for c in state.conflicts:
        if c.conflict_id in resolved_ids:
            c.status = ConflictStatus.RESOLVED

    return state


def node_mark_human_review(state: SharedBusinessState) -> SharedBusinessState:
    """
    Node: mark_human_review
    Sets state.status = HUMAN_REVIEW_REQUIRED when significant unresolved conflicts
    remain after negotiation. Does NOT synthesize — synthesis still runs afterwards
    with dissent fully preserved.
    """
    state.status = StateStatus.HUMAN_REVIEW_REQUIRED
    return state


def node_synthesize(state: SharedBusinessState) -> SharedBusinessState:
    """
    Node: synthesize
    Derives FinalDecision from the full structured state using a deterministic
    rule cascade (Rules A–F). No votes are counted. Each decision step is
    traceable to named model fields.
    """
    state.final_decision = _build_final_decision(state)
    if state.status != StateStatus.HUMAN_REVIEW_REQUIRED:
        state.status = StateStatus.COMPLETED
    else:
        # Human review required: status stays HUMAN_REVIEW_REQUIRED but
        # we still populate the final_decision for traceability.
        # Mark it completed after writing the decision.
        state.status = StateStatus.COMPLETED
    return state


# ---------------------------------------------------------------------------
# Conditional Edge Routers
# ---------------------------------------------------------------------------

def route_after_detection(state: SharedBusinessState) -> Literal["negotiate", "synthesize"]:
    """
    After first-pass conflict detection:
    - Route to negotiation if any open conflicts exist.
    - Route directly to synthesis if the pipeline is conflict-free.
    """
    open_conflicts = [c for c in state.conflicts if c.status == ConflictStatus.OPEN]
    if open_conflicts:
        return "negotiate"
    return "synthesize"


def route_after_recheck(
    state: SharedBusinessState,
) -> Literal["mark_human_review", "synthesize"]:
    """
    After post-negotiation re-check:
    - Route to mark_human_review if ≥1 significant (high/critical + UNRESOLVED)
      conflict remains after negotiation.
    - Route to synthesize for resolved or only low/medium unresolved conflicts.
    """
    significant = [c for c in state.conflicts if _is_significant_unresolved(c)]
    if significant:
        return "mark_human_review"
    return "synthesize"


# ---------------------------------------------------------------------------
# Synthesis: FinalDecision Builder
# ---------------------------------------------------------------------------

def _build_final_decision(state: SharedBusinessState) -> FinalDecision:
    """
    Builds FinalDecision from the structured SharedBusinessState.

    Uses final effective positions (revised_positions if populated, else agent_positions).
    Applies deterministic Rule Cascade A–F for recommendation.
    Computes an aggregate analytical confidence indicator (NOT a business success probability).
    """
    effective: List[AgentPosition] = (
        state.revised_positions if state.revised_positions else state.agent_positions
    )

    # -----------------------------------------------------------------------
    # Rule Cascade A–F: Determine recommendation
    # -----------------------------------------------------------------------
    recommendation = _determine_recommendation(state, effective)

    # -----------------------------------------------------------------------
    # Confidence: Aggregate Analytical Indicator
    # -----------------------------------------------------------------------
    confidence = _compute_confidence(state, effective)

    # -----------------------------------------------------------------------
    # key_factors: Top claim per agent + canonical facts
    # -----------------------------------------------------------------------
    key_factors: List[str] = []
    for pos in effective:
        if pos.key_claims:
            key_factors.append(pos.key_claims[0].claim)
    key_factors.extend(state.canonical_facts[:3])  # top 3 canonical facts

    # -----------------------------------------------------------------------
    # evidence_trace: All evidence items + negotiation evidence exchanged
    # -----------------------------------------------------------------------
    evidence_trace: List[str] = []
    for pos in effective:
        evidence_trace.extend(pos.evidence)
    for rnd in state.negotiation_history:
        evidence_trace.extend(rnd.evidence_exchanged)
    evidence_trace = list(dict.fromkeys(evidence_trace))  # deduplicate, preserve order

    # -----------------------------------------------------------------------
    # risks: Union of all agent risks
    # -----------------------------------------------------------------------
    risks: List[str] = []
    for pos in effective:
        risks.extend(pos.risks)
    risks = list(dict.fromkeys(risks))

    # -----------------------------------------------------------------------
    # action_plan: Union of all recommended_actions
    # -----------------------------------------------------------------------
    action_plan: List[str] = []
    for pos in effective:
        action_plan.extend(pos.recommended_actions)
    action_plan = list(dict.fromkeys(action_plan))

    # -----------------------------------------------------------------------
    # alternatives_considered: Derived from open questions
    # -----------------------------------------------------------------------
    alternatives_considered: List[str] = list(state.open_questions)

    # -----------------------------------------------------------------------
    # trade_offs: From resolved conflict resolution summaries
    # -----------------------------------------------------------------------
    trade_offs: List[str] = []
    for c in state.conflicts:
        if c.status == ConflictStatus.RESOLVED and c.resolution:
            trade_offs.append(c.resolution)

    # -----------------------------------------------------------------------
    # assumptions: Union of all agent assumptions (deduplicated)
    # -----------------------------------------------------------------------
    assumptions: List[str] = []
    for pos in effective:
        assumptions.extend(pos.assumptions)
    assumptions = list(dict.fromkeys(assumptions))

    # -----------------------------------------------------------------------
    # unresolved_dissent: Preserved minority dissent from unresolved conflicts
    # -----------------------------------------------------------------------
    unresolved_dissent: List[str] = []
    for c in state.conflicts:
        if c.status == ConflictStatus.UNRESOLVED:
            unresolved_dissent.extend(c.conflicting_claims)
    for rnd in state.negotiation_history:
        unresolved_dissent.extend(rnd.unresolved_points)
    unresolved_dissent = list(dict.fromkeys(unresolved_dissent))

    # -----------------------------------------------------------------------
    # rationale: Human-readable explanation of the recommendation
    # -----------------------------------------------------------------------
    rationale = _build_rationale(state, recommendation, effective)

    return FinalDecision(
        recommendation=recommendation,
        rationale=rationale,
        confidence=confidence,
        key_factors=key_factors,
        alternatives_considered=alternatives_considered,
        trade_offs=trade_offs,
        risks=risks,
        assumptions=assumptions,
        unresolved_dissent=unresolved_dissent,
        action_plan=action_plan,
        evidence_trace=evidence_trace,
    )


def _determine_recommendation(
    state: SharedBusinessState, effective: List[AgentPosition]
) -> PositionType:
    """
    Deterministic rule cascade A–F. No votes counted. Stop at first matching rule.
    Each rule inspects named model fields directly.
    """
    if not effective:
        return PositionType.INSUFFICIENT_EVIDENCE

    significant_unresolved = [c for c in state.conflicts if _is_significant_unresolved(c)]
    all_resolved = all(
        c.status in (ConflictStatus.RESOLVED, ConflictStatus.UNRESOLVED)
        for c in state.conflicts
    )
    positions_set = {p.position for p in effective}

    # -----------------------------------------------------------------------
    # Rule A: Significant unresolved conflicts (high/critical severity)
    # -----------------------------------------------------------------------
    if significant_unresolved:
        # Check if any involve a hard constraint violation
        canonical_constraints_lower = [c.lower() for c in state.constraints]
        hard_constraint_breach = False
        for conflict in significant_unresolved:
            for claim in conflict.conflicting_claims:
                claim_lower = claim.lower()
                for canon in canonical_constraints_lower:
                    if any(
                        kw in canon and any(bk in claim_lower for bk in ("exceed", "violat", "breach", "beyond", "impossible"))
                        for kw in ("budget", "regulat", "cap", "limit", "max", "compliance")
                    ):
                        hard_constraint_breach = True
                        break
        return PositionType.DO_NOT_RECOMMEND if hard_constraint_breach else PositionType.CONDITIONAL

    # -----------------------------------------------------------------------
    # Rule B: Hard constraint violation detected in agent risk/constraint data
    # -----------------------------------------------------------------------
    for pos in effective:
        combined = " ".join(pos.constraints_assumed + pos.risks).lower()
        constraint_keywords = ("budget exceeded", "violat", "regulatory block", "non-compliant",
                                "cannot proceed", "cap exceeded", "hard limit")
        if any(kw in combined for kw in constraint_keywords):
            # Check if any negotiation resolution mitigates it
            if state.negotiation_history:
                # Negotiation produced some resolution — conditionally proceed
                return PositionType.CONDITIONAL
            return PositionType.DO_NOT_RECOMMEND

    # -----------------------------------------------------------------------
    # Rule C: Full alignment of all effective positions
    # -----------------------------------------------------------------------
    if len(positions_set) == 1:
        return next(iter(positions_set))

    # -----------------------------------------------------------------------
    # Rule D: Conflicts existed but all resolved by negotiation
    # -----------------------------------------------------------------------
    if state.conflicts and all(c.status == ConflictStatus.RESOLVED for c in state.conflicts):
        # Re-apply Rule C on revised positions
        revised_positions_set = {p.position for p in effective}
        if len(revised_positions_set) == 1:
            return next(iter(revised_positions_set))
        # Mixed revised positions — treat as conditional with trade-offs noted
        return PositionType.CONDITIONAL

    # -----------------------------------------------------------------------
    # Rule E: Insufficient evidence coverage
    # -----------------------------------------------------------------------
    insufficient_count = sum(
        1 for p in effective if p.position == PositionType.INSUFFICIENT_EVIDENCE
    )
    failed_count = sum(1 for rec in state.execution_log if not rec.success)

    if insufficient_count >= 2 or failed_count >= 2:
        return PositionType.INSUFFICIENT_EVIDENCE
    if insufficient_count == 1 and len(positions_set) > 1:
        return PositionType.CONDITIONAL

    # -----------------------------------------------------------------------
    # Rule F: Fallback — mixed positions, low/medium unresolved conflicts
    # -----------------------------------------------------------------------
    return PositionType.CONDITIONAL


def _compute_confidence(
    state: SharedBusinessState, effective: List[AgentPosition]
) -> float:
    """
    Aggregate analytical confidence indicator.
    Reflects the degree of analytical certainty across the agent collaboration.
    Does NOT represent a probability of business success or startup viability.

    Base: mean of agent position confidence scores.
    Adjustments: unresolved significant conflicts, failed agents,
    insufficient evidence, position disagreement, full negotiation resolution.
    Final value clamped to [0.0, 1.0].
    """
    if not effective:
        return 0.0

    # Base: mean confidence across contributing agents
    base = sum(p.confidence for p in effective) / len(effective)

    significant_unresolved_count = sum(
        1 for c in state.conflicts if _is_significant_unresolved(c)
    )
    failed_count = sum(1 for rec in state.execution_log if not rec.success)
    insufficient_count = sum(
        1 for p in effective if p.position == PositionType.INSUFFICIENT_EVIDENCE
    )
    positions_set = {p.position for p in effective}
    positions_agree = len(positions_set) == 1
    all_conflicts_resolved = state.conflicts and all(
        c.status == ConflictStatus.RESOLVED for c in state.conflicts
    )

    adjustment = 0.0
    # Deductions
    adjustment -= 0.05 * significant_unresolved_count   # analytical uncertainty from unresolved high-severity conflicts
    adjustment -= 0.03 * failed_count                   # reduced domain coverage
    adjustment -= 0.04 if insufficient_count >= 2 else 0.0  # weak evidence base
    adjustment -= 0.03 if not positions_agree else 0.0  # analytical divergence across agents
    # Bonus
    adjustment += 0.03 if all_conflicts_resolved else 0.0  # improved analytical consensus

    return max(0.0, min(1.0, base + adjustment))


def _build_rationale(
    state: SharedBusinessState,
    recommendation: PositionType,
    effective: List[AgentPosition],
) -> str:
    """
    Builds a human-readable rationale string explaining how the recommendation
    was derived from the structured state data.
    """
    goal = state.business_context.primary_goal or "the stated objective"
    business_name = state.business_context.business_name or "the venture"
    agent_count = len(effective)
    failed_count = sum(1 for rec in state.execution_log if not rec.success)
    conflict_count = len(state.conflicts)
    resolved_count = sum(1 for c in state.conflicts if c.status == ConflictStatus.RESOLVED)
    unresolved_sig_count = sum(1 for c in state.conflicts if _is_significant_unresolved(c))
    negotiation_rounds = len(state.negotiation_history)

    parts = [
        f"Multi-agent collaborative analysis of '{business_name}' "
        f"regarding '{goal}' completed with {agent_count} specialist agent(s) contributing positions.",
    ]

    if failed_count:
        parts.append(
            f"{failed_count} agent(s) encountered execution errors; their domain perspective "
            f"is absent from this analysis (see execution_log for details)."
        )

    if conflict_count:
        parts.append(
            f"{conflict_count} inter-agent conflict(s) were detected. "
            f"{negotiation_rounds} negotiation round(s) were conducted. "
            f"{resolved_count} conflict(s) were resolved."
        )

    if unresolved_sig_count:
        parts.append(
            f"{unresolved_sig_count} significant unresolved conflict(s) of high or critical severity "
            f"remain after negotiation. These materially affect the recommendation and are "
            f"preserved in unresolved_dissent."
        )

    rec_map = {
        PositionType.RECOMMEND: "proceed with the proposed strategy",
        PositionType.DO_NOT_RECOMMEND: "not proceed as currently structured due to unmitigated constraint violations or critical risks",
        PositionType.CONDITIONAL: "proceed conditionally — key trade-offs, constraints, or dissent must be addressed before commitment",
        PositionType.INSUFFICIENT_EVIDENCE: "defer the decision — insufficient evidence across critical domains prevents a reliable recommendation",
    }
    parts.append(
        f"Based on structural analysis of agent positions, conflict outcomes, and constraint satisfaction, "
        f"the collaborative recommendation is to {rec_map.get(recommendation, recommendation.value)}."
    )

    if state.status == StateStatus.HUMAN_REVIEW_REQUIRED:
        parts.append(
            "Human expert review is required before final commitment due to unresolved significant conflicts."
        )

    return " ".join(parts)


# ---------------------------------------------------------------------------
# OrchestratorAgent: Graph Builder & Runner
# ---------------------------------------------------------------------------

class OrchestratorAgent:
    """
    Orchestrator & Synthesis Coordination Agent.

    Builds and compiles a LangGraph StateGraph that implements the full
    multi-agent coordination pipeline as an explicit state machine.

    Usage:
        agent = OrchestratorAgent()
        final_state = agent.run(business_context)
    """

    def __init__(self) -> None:
        self._graph: CompiledStateGraph = self._build_graph()

    def _build_graph(self) -> CompiledStateGraph:
        """Constructs and compiles the LangGraph StateGraph."""
        builder = StateGraph(SharedBusinessState)

        # Register nodes
        builder.add_node("initialize_state", node_initialize_state)
        builder.add_node("run_specialists", node_run_specialists)
        builder.add_node("detect_conflicts", node_detect_conflicts)
        builder.add_node("negotiate", node_negotiate)
        builder.add_node("recheck_conflicts", node_recheck_conflicts)
        builder.add_node("mark_human_review", node_mark_human_review)
        builder.add_node("synthesize", node_synthesize)

        # Entry point
        builder.set_entry_point("initialize_state")

        # Linear edges
        builder.add_edge("initialize_state", "run_specialists")
        builder.add_edge("run_specialists", "detect_conflicts")

        # Conditional edge: after first-pass detection
        builder.add_conditional_edges(
            "detect_conflicts",
            route_after_detection,
            {
                "negotiate": "negotiate",
                "synthesize": "synthesize",
            },
        )

        # After negotiation: always re-check
        builder.add_edge("negotiate", "recheck_conflicts")

        # Conditional edge: after post-negotiation re-check
        builder.add_conditional_edges(
            "recheck_conflicts",
            route_after_recheck,
            {
                "mark_human_review": "mark_human_review",
                "synthesize": "synthesize",
            },
        )

        # Human review always feeds into synthesis (dissent is preserved)
        builder.add_edge("mark_human_review", "synthesize")

        # Terminal node
        builder.add_edge("synthesize", END)

        return builder.compile()

    def run(self, context: BusinessContext) -> SharedBusinessState:
        """
        Runs the full multi-agent pipeline for the given BusinessContext.

        Returns the final SharedBusinessState with final_decision populated
        and the complete collaboration trace (agent_positions, conflicts,
        negotiation_history, revised_positions, execution_log).
        """
        import uuid

        # Bootstrap the initial state — graph nodes will populate derived fields
        initial_state = SharedBusinessState(
            run_id=f"run-{uuid.uuid4().hex[:12]}",
            business_context=context,
        )

        # LangGraph returns a plain dict when the state schema is a Pydantic model.
        # Validate and convert it back to SharedBusinessState for a typed return value.
        raw: dict = self._graph.invoke(initial_state)
        if isinstance(raw, SharedBusinessState):
            return raw
        return SharedBusinessState.model_validate(raw)
