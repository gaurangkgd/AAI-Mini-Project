import pytest
from fastapi.testclient import TestClient
from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType, ClaimItem
from app.models.state import SharedBusinessState, StateStatus, ConflictType, ConflictStatus
from app.coordination.shared_goal import SharedGoalConsistencyAgent
from app.coordination.conflict_detection import ConflictDetectionAgent
from app.main import app

client = TestClient(app)


def _create_sample_state() -> SharedBusinessState:
    ctx = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        business_name="SolarDrone",
        primary_goal="Assess market entry",
        constraints=["Max budget limit of 15 Lakhs"],
    )
    agent = SharedGoalConsistencyAgent()
    return agent.initialize_state(ctx)


def test_no_conflicts_aligned_positions():
    state = _create_sample_state()
    agent = ConflictDetectionAgent()

    pos1 = AgentPosition(
        agent_name="Market Research Agent",
        position=PositionType.RECOMMEND,
        confidence=0.85,
        assumptions=["Market demand is adequate."],
    )
    pos2 = AgentPosition(
        agent_name="Customer Agent",
        position=PositionType.RECOMMEND,
        confidence=0.80,
        assumptions=["Target customer interest is adequate."],
    )

    conflicts = agent.detect_conflicts(state, [pos1, pos2])
    assert len(conflicts) == 0
    assert state.status == StateStatus.INITIALIZED
    assert len(state.conflicts) == 0


def test_position_conflict_direct_opposite():
    state = _create_sample_state()
    agent = ConflictDetectionAgent()

    pos_fin = AgentPosition(
        agent_name="Financial Agent",
        position=PositionType.DO_NOT_RECOMMEND,
        confidence=0.90,
        evidence=["Burn rate exceeds capital runway."],
    )
    pos_mkt = AgentPosition(
        agent_name="Market Research Agent",
        position=PositionType.RECOMMEND,
        confidence=0.85,
        evidence=["High TAM growth."],
    )

    conflicts = agent.detect_conflicts(state, [pos_fin, pos_mkt])
    assert len(conflicts) == 1
    cnf = conflicts[0]
    assert cnf.conflict_type == ConflictType.POSITION_CONFLICT
    assert cnf.severity == "high"
    assert cnf.status == ConflictStatus.OPEN
    assert "Financial Agent" in cnf.agents_involved
    assert "Market Research Agent" in cnf.agents_involved
    assert state.status == StateStatus.CONFLICT_DETECTED
    assert len(state.conflicts) == 1


def test_position_conflict_partial():
    state = _create_sample_state()
    agent = ConflictDetectionAgent()

    pos_mkt = AgentPosition(
        agent_name="Market Research Agent",
        position=PositionType.RECOMMEND,
        confidence=0.85,
    )
    pos_ops = AgentPosition(
        agent_name="Operations Agent",
        position=PositionType.CONDITIONAL,
        confidence=0.75,
    )

    conflicts = agent.detect_conflicts(state, [pos_mkt, pos_ops])
    assert len(conflicts) == 1
    cnf = conflicts[0]
    assert cnf.conflict_type == ConflictType.POSITION_CONFLICT
    assert cnf.severity == "medium"


def test_assumption_conflict():
    state = _create_sample_state()
    agent = ConflictDetectionAgent()

    pos_fin = AgentPosition(
        agent_name="Financial Agent",
        position=PositionType.CONDITIONAL,
        confidence=0.75,
        assumptions=["Capital budget is sufficient for launch."],
    )
    pos_ops = AgentPosition(
        agent_name="Operations Agent",
        position=PositionType.CONDITIONAL,
        confidence=0.75,
        assumptions=["Capital budget is insufficient for logistics fleet."],
    )

    conflicts = agent.detect_conflicts(state, [pos_fin, pos_ops])
    assert len(conflicts) > 0
    assumption_cnfs = [c for c in conflicts if c.conflict_type == ConflictType.ASSUMPTION_CONFLICT]
    assert len(assumption_cnfs) > 0
    assert assumption_cnfs[0].severity == "medium"


def test_constraint_conflict():
    state = _create_sample_state()
    agent = ConflictDetectionAgent()

    pos_ops = AgentPosition(
        agent_name="Operations Agent",
        position=PositionType.CONDITIONAL,
        confidence=0.70,
        constraints_assumed=["Capital expenditure exceeds budget limit"],
    )
    pos_mkt = AgentPosition(
        agent_name="Market Research Agent",
        position=PositionType.CONDITIONAL,
        confidence=0.80,
    )

    conflicts = agent.detect_conflicts(state, [pos_ops, pos_mkt])
    constraint_cnfs = [c for c in conflicts if c.conflict_type == ConflictType.CONSTRAINT_CONFLICT]
    assert len(constraint_cnfs) > 0
    assert constraint_cnfs[0].severity in ["high", "medium"]


def test_evidence_conflict():
    state = _create_sample_state()
    agent = ConflictDetectionAgent()

    pos_mkt = AgentPosition(
        agent_name="Market Research Agent",
        position=PositionType.CONDITIONAL,
        confidence=0.80,
        key_claims=[
            ClaimItem(
                claim="Validated strong demand in renewable sector.",
                confidence=0.85,
            )
        ],
    )
    pos_cust = AgentPosition(
        agent_name="Customer Agent",
        position=PositionType.CONDITIONAL,
        confidence=0.40,
        key_claims=[
            ClaimItem(
                claim="Missing customer demand validation in target segment.",
                confidence=0.90,
            )
        ],
    )

    conflicts = agent.detect_conflicts(state, [pos_mkt, pos_cust])
    evidence_cnfs = [c for c in conflicts if c.conflict_type == ConflictType.EVIDENCE_CONFLICT]
    assert len(evidence_cnfs) > 0
    assert evidence_cnfs[0].severity == "low"


def test_conflict_ids_and_state_storage():
    state = _create_sample_state()
    agent = ConflictDetectionAgent()

    pos1 = AgentPosition(agent_name="A1", position=PositionType.RECOMMEND, confidence=0.8)
    pos2 = AgentPosition(agent_name="A2", position=PositionType.DO_NOT_RECOMMEND, confidence=0.9)

    conflicts = agent.detect_conflicts(state, [pos1, pos2])
    assert len(conflicts) > 0
    for c in conflicts:
        assert c.conflict_id.startswith("cnf-")
        assert c.status == ConflictStatus.OPEN

    assert state.status == StateStatus.CONFLICT_DETECTED
    assert state.conflicts == conflicts


def test_api_detect_conflicts_endpoint():
    goal_agent = SharedGoalConsistencyAgent()
    ctx = BusinessContext(mode=BusinessMode.NEW_STARTUP, primary_goal="API Conflict Test")
    state = goal_agent.initialize_state(ctx)

    pos1 = AgentPosition(agent_name="Financial Agent", position=PositionType.DO_NOT_RECOMMEND, confidence=0.9)
    pos2 = AgentPosition(agent_name="Market Research Agent", position=PositionType.RECOMMEND, confidence=0.85)

    payload = {
        "state": state.model_dump(),
        "positions": [pos1.model_dump(), pos2.model_dump()],
    }

    response = client.post("/api/coordination/conflicts/detect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0
    assert data["status"] == "conflict_detected"
    assert len(data["conflicts"]) > 0
    assert data["conflicts"][0]["conflict_type"] == "position_conflict"
