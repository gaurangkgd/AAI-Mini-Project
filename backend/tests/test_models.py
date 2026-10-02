import pytest
from pydantic import ValidationError

from app.models.business import BusinessMode, BusinessContext
from app.models.agent import PositionType, ClaimItem, AgentPosition
from app.models.state import (
    ConflictType,
    ConflictStatus,
    Conflict,
    NegotiationRound,
    FinalDecision,
    StateStatus,
    SharedBusinessState,
)


def test_valid_new_startup_input():
    """Test creating a BusinessContext model for a new startup idea."""
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        business_name="EcoClean Tech",
        business_idea="AI-driven waterless solar panel cleaning drone system",
        industry="CleanTech",
        primary_goal="Validate market feasibility and financial model",
        budget=1500000.0,
        currency="INR",
        time_horizon="6 months",
        constraints=["Bootstrapped limit of 15 Lakhs"],
    )
    assert context.mode == BusinessMode.NEW_STARTUP
    assert context.business_name == "EcoClean Tech"
    assert context.budget == 1500000.0
    assert context.currency == "INR"
    assert len(context.constraints) == 1


def test_valid_existing_business_input():
    """Test creating a BusinessContext model for an existing business decision."""
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_name="Acme Logistics Inc.",
        industry="Logistics",
        business_stage="Growth",
        primary_goal="Evaluate expansion into cold-chain warehouse automation",
        budget=5000000.0,
        current_problems=["Rising fuel costs"],
        existing_metrics={"ARR": "12,000,000 INR", "fleet_count": 45},
    )
    assert context.mode == BusinessMode.EXISTING_BUSINESS
    assert context.business_name == "Acme Logistics Inc."
    assert context.existing_metrics["fleet_count"] == 45
    assert len(context.current_problems) == 1


def test_invalid_mode():
    """Test that an invalid mode value raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        BusinessContext(
            mode="invalid_mode",
            primary_goal="Test invalid mode",
        )
    assert "mode" in str(exc_info.value)


def test_invalid_confidence_value():
    """Test that a confidence value outside [0.0, 1.0] raises a ValidationError."""
    with pytest.raises(ValidationError):
        AgentPosition(
            agent_name="Financial Agent",
            position=PositionType.RECOMMEND,
            confidence=1.5,  # Greater than 1.0
        )

    with pytest.raises(ValidationError):
        AgentPosition(
            agent_name="Financial Agent",
            position=PositionType.RECOMMEND,
            confidence=-0.1,  # Less than 0.0
        )

    with pytest.raises(ValidationError):
        ClaimItem(
            claim="High revenue potential",
            confidence=1.2,
        )


def test_invalid_agent_position_type():
    """Test that an unrecognized position string raises a ValidationError."""
    with pytest.raises(ValidationError):
        AgentPosition(
            agent_name="Market Research Agent",
            position="strongly_agree",  # Not a valid PositionType enum
            confidence=0.8,
        )


def test_conflict_creation():
    """Test Conflict model creation and default status."""
    conflict = Conflict(
        conflict_id="cnf-001",
        agents_involved=["Financial Agent", "Marketing & GTM Agent"],
        conflict_type=ConflictType.PRIORITY_CONFLICT,
        description="Disagreement on CAC allocation vs payback period horizon",
        conflicting_claims=[
            "Financial Agent claims payback > 18 months is unsustainable",
            "Marketing Agent claims CAC requires 24 months for brand traction",
        ],
    )
    assert conflict.conflict_id == "cnf-001"
    assert conflict.status == ConflictStatus.OPEN
    assert conflict.severity == "medium"
    assert len(conflict.agents_involved) == 2


def test_shared_business_state_creation():
    """Test complete SharedBusinessState creation with nested models."""
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        business_name="TestStartup",
        primary_goal="Assess market entry",
    )

    agent_pos = AgentPosition(
        agent_name="Market Research Agent",
        position=PositionType.RECOMMEND,
        confidence=0.85,
        key_claims=[
            ClaimItem(
                claim="Target TAM is growing at 18% CAGR",
                source="Industry Report 2025",
                confidence=0.9,
            )
        ],
    )

    state = SharedBusinessState(
        run_id="run-12345",
        business_context=context,
        agent_positions=[agent_pos],
        status=StateStatus.INITIALIZED,
    )

    assert state.run_id == "run-12345"
    assert state.business_context.business_name == "TestStartup"
    assert state.status == StateStatus.INITIALIZED
    assert len(state.agent_positions) == 1
    assert state.agent_positions[0].confidence == 0.85
