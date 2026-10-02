import pytest
from fastapi.testclient import TestClient

from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType, ClaimItem
from app.models.state import SharedBusinessState, Conflict, ConflictType, ConflictStatus, StateStatus
from app.coordination.shared_goal import SharedGoalConsistencyAgent
from app.coordination.conflict_detection import ConflictDetectionAgent
from app.coordination.negotiation import NegotiationAgent
from app.coordination.orchestrator import OrchestratorAgent
from app.main import app

client = TestClient(app)


def _setup_initial_state() -> SharedBusinessState:
    ctx = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        business_name="EcoClean Tech",
        primary_goal="Assess market launch feasibility",
        budget=1500000.0,
    )
    goal_agent = SharedGoalConsistencyAgent()
    return goal_agent.initialize_state(ctx)


def test_negotiation_agent_instantiation():
    agent = NegotiationAgent()
    assert agent is not None


def test_negotiation_no_open_conflicts():
    state = _setup_initial_state()
    agent = NegotiationAgent()

    pos1 = AgentPosition(agent_name="Market Research Agent", position=PositionType.RECOMMEND, confidence=0.8)
    pos2 = AgentPosition(agent_name="Customer Agent", position=PositionType.RECOMMEND, confidence=0.8)

    updated_state, rounds = agent.run_negotiation(state, [pos1, pos2], [])
    assert len(rounds) == 0
    assert len(updated_state.negotiation_history) == 0


def test_resolvable_conflict_negotiation():
    state = _setup_initial_state()
    state.agent_positions = [
        AgentPosition(
            agent_name="Financial Agent",
            position=PositionType.DO_NOT_RECOMMEND,
            confidence=0.90,
            assumptions=["Burn rate is unsustainable."],
            evidence=["CapEx limits exceeded."],
        ),
        AgentPosition(
            agent_name="Market Research Agent",
            position=PositionType.RECOMMEND,
            confidence=0.85,
            assumptions=["Market demand justifies pilot rollout."],
            evidence=["Phased pilot rollout proposed to cap initial expenditure."],
            recommended_actions=["Run phased pilot rollout with 15 solar operators."],
        ),
    ]

    detector = ConflictDetectionAgent()
    conflicts = detector.detect_conflicts(state, state.agent_positions)
    assert len(conflicts) > 0

    negotiator = NegotiationAgent()
    updated_state, rounds = negotiator.run_negotiation(state, state.agent_positions, conflicts)

    assert len(rounds) > 0
    round1 = rounds[0]
    assert "Financial Agent" in round1.participants
    assert "Market Research Agent" in round1.participants
    assert len(round1.previous_positions) == 2
    assert len(round1.evidence_exchanged) == 2
    assert len(round1.arguments) == 2

    # Check position revision: Financial Agent DO_NOT_RECOMMEND -> CONDITIONAL
    revised_fin = [p for p in updated_state.revised_positions if p.agent_name == "Financial Agent"][0]
    assert revised_fin.position == PositionType.CONDITIONAL

    # Original position remains preserved
    orig_fin = [p for p in updated_state.agent_positions if p.agent_name == "Financial Agent"][0]
    assert orig_fin.position == PositionType.DO_NOT_RECOMMEND

    # Conflict status resolved
    pos_conflict = [c for c in conflicts if c.conflict_type == ConflictType.POSITION_CONFLICT][0]
    assert pos_conflict.status == ConflictStatus.RESOLVED
    assert pos_conflict.resolution is not None


def test_unresolved_conflict_dissent_preservation():
    state = _setup_initial_state()
    pos_fin = AgentPosition(
        agent_name="Financial Agent",
        position=PositionType.DO_NOT_RECOMMEND,
        confidence=0.95,
        assumptions=["Burn rate unsustainable."],
        evidence=["Zero cash runway."],
    )
    pos_mkt = AgentPosition(
        agent_name="Market Research Agent",
        position=PositionType.RECOMMEND,
        confidence=0.90,
        assumptions=["TAM is massive."],
        evidence=["Market report 2026."],
    )
    state.agent_positions = [pos_fin, pos_mkt]

    conflict = Conflict(
        conflict_id="cnf-test-unresolved",
        agents_involved=["Financial Agent", "Market Research Agent"],
        conflict_type=ConflictType.POSITION_CONFLICT,
        description="Fundamental disagreement on burn rate vs TAM",
        severity="high",
        status=ConflictStatus.OPEN,
    )

    negotiator = NegotiationAgent()
    updated_state, rounds = negotiator.run_negotiation(state, [pos_fin, pos_mkt], [conflict])

    assert len(rounds) == 1
    round1 = rounds[0]
    assert conflict.status == ConflictStatus.UNRESOLVED
    assert conflict.resolution is None
    assert len(round1.unresolved_points) > 0
    assert updated_state.status == StateStatus.NEGOTIATING


def test_negotiation_history_not_mutated_by_subsequent_revisions():
    """
    Verifies that when multiple conflicts are processed across rounds,
    a position revision in Round 1 updates Round 2's starting state without
    mutating Round 1's previous_positions or arguments.
    """
    state = _setup_initial_state()
    pos_fin = AgentPosition(
        agent_name="Financial Agent",
        position=PositionType.DO_NOT_RECOMMEND,
        confidence=0.90,
        evidence=["High burn rate."],
        assumptions=["Capital depleted."],
    )
    pos_mkt = AgentPosition(
        agent_name="Market Research Agent",
        position=PositionType.RECOMMEND,
        confidence=0.85,
        evidence=["Phased pilot rollout proposed to test market."],
        recommended_actions=["Run pilot rollout with 15 operators."],
    )
    pos_comp = AgentPosition(
        agent_name="Competition Agent",
        position=PositionType.CONDITIONAL,
        confidence=0.77,
        evidence=["Moderate competition."],
    )

    positions = [pos_fin, pos_mkt, pos_comp]

    conflict1 = Conflict(
        conflict_id="cnf-1",
        agents_involved=["Financial Agent", "Market Research Agent"],
        conflict_type=ConflictType.POSITION_CONFLICT,
        description="Financial Agent is DO_NOT_RECOMMEND while Market Research Agent is RECOMMEND",
        severity="high",
        status=ConflictStatus.OPEN,
    )
    conflict2 = Conflict(
        conflict_id="cnf-2",
        agents_involved=["Financial Agent", "Competition Agent"],
        conflict_type=ConflictType.POSITION_CONFLICT,
        description="Financial Agent is DO_NOT_RECOMMEND while Competition Agent is CONDITIONAL",
        severity="medium",
        status=ConflictStatus.OPEN,
    )

    negotiator = NegotiationAgent()
    updated_state, rounds = negotiator.run_negotiation(state, positions, [conflict1, conflict2])

    assert len(rounds) == 2

    # Round 1: Financial Agent started at DO_NOT_RECOMMEND
    r1 = rounds[0]
    r1_fin_prev = [p for p in r1.previous_positions if p.agent_name == "Financial Agent"][0]
    assert r1_fin_prev.position == PositionType.DO_NOT_RECOMMEND
    assert any("DO_NOT_RECOMMEND" in arg for arg in r1.arguments if "Financial Agent" in arg)

    # Round 2: Financial Agent started at CONDITIONAL (the revised position from Round 1)
    r2 = rounds[1]
    r2_fin_prev = [p for p in r2.previous_positions if p.agent_name == "Financial Agent"][0]
    assert r2_fin_prev.position == PositionType.CONDITIONAL
    assert any("CONDITIONAL" in arg for arg in r2.arguments if "Financial Agent" in arg)

    # Confirm Round 1 was NOT retroactively mutated
    assert r1_fin_prev.position == PositionType.DO_NOT_RECOMMEND


def test_revised_positions_preserves_specialist_ordering():
    """
    Verifies state.revised_positions maintains the exact order of the incoming positions list.
    """
    state = _setup_initial_state()
    agent_names = [
        "Market Research Agent",
        "Financial Agent",
        "Competition Agent",
        "Customer Agent",
        "Marketing & GTM Agent",
        "Operations Agent",
        "Risk & Regulatory Agent",
    ]
    positions = [
        AgentPosition(agent_name=name, position=PositionType.CONDITIONAL, confidence=0.8)
        for name in agent_names
    ]

    negotiator = NegotiationAgent()
    updated_state, _ = negotiator.run_negotiation(state, positions, [])

    # Order must match incoming specialist list exactly
    revised_names = [p.agent_name for p in updated_state.revised_positions]
    assert revised_names == agent_names


def test_quicklearn_negotiation_history_internal_consistency():
    """
    Runs the full QuickLearn orchestrator flow and verifies every negotiation round
    has 100% internal consistency between previous_positions, arguments, and resolution.
    """
    quicklearn_context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_name="QuickLearn",
        industry="EdTech",
        business_stage="Growth",
        business_model="Subscription",
        target_market="College students aged 18-24 across India",
        budget=500000.0,
        currency="INR",
        time_horizon="6 months",
        primary_goal="Decide whether to reduce the subscription price by 50% to rapidly increase the number of users while maintaining profitability.",
        constraints=[
            "Current cash reserves are limited",
            "Need to maintain positive cash flow",
            "Management wants 3x user growth within 6 months",
            "Cannot significantly increase marketing spending",
            "Current customer acquisition cost is already high",
            "Existing subscribers are sensitive to price changes",
        ],
        additional_context="The company currently has 10,000 paying subscribers at INR 500 per month. Management wants to reduce the price to INR 250 to attract more students and compete with lower-priced alternatives. However, the company has limited cash reserves and cannot significantly increase spending on marketing or infrastructure. The goal is to triple the user base within 6 months while maintaining positive cash flow.",
    )

    orchestrator = OrchestratorAgent()
    state = orchestrator.run(quicklearn_context)

    assert len(state.negotiation_history) > 0
    for round_rec in state.negotiation_history:
        # Check that previous_positions matches the round arguments
        for prev_pos in round_rec.previous_positions:
            agent_arg = [arg for arg in round_rec.arguments if prev_pos.agent_name in arg]
            assert len(agent_arg) > 0
            # Stance in arguments must match previous_positions stance
            expected_stance = prev_pos.position.value.upper()
            assert expected_stance in agent_arg[0], (
                f"Round {round_rec.round_number} argument '{agent_arg[0]}' does not match "
                f"starting stance {expected_stance} for {prev_pos.agent_name}"
            )


def test_api_negotiation_run_endpoint():
    goal_agent = SharedGoalConsistencyAgent()
    ctx = BusinessContext(mode=BusinessMode.NEW_STARTUP, primary_goal="Negotiation API Test")
    state = goal_agent.initialize_state(ctx)

    pos1 = AgentPosition(
        agent_name="Financial Agent",
        position=PositionType.DO_NOT_RECOMMEND,
        confidence=0.9,
        evidence=["CapEx limit exceeded."],
    )
    pos2 = AgentPosition(
        agent_name="Market Research Agent",
        position=PositionType.RECOMMEND,
        confidence=0.85,
        evidence=["Phased pilot rollout proposed."],
    )

    detector = ConflictDetectionAgent()
    conflicts = detector.detect_conflicts(state, [pos1, pos2])

    payload = {
        "state": state.model_dump(),
        "positions": [pos1.model_dump(), pos2.model_dump()],
        "conflicts": [c.model_dump() for c in conflicts],
    }

    response = client.post("/api/coordination/negotiation/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "state" in data
    assert "negotiation_rounds" in data
    assert len(data["negotiation_rounds"]) > 0
    assert data["resolved_conflicts"] + data["unresolved_conflicts"] == len(conflicts)
