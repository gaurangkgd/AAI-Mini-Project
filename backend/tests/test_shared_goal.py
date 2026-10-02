import pytest
from app.models.business import BusinessContext, BusinessMode
from app.models.state import SharedBusinessState, StateStatus
from app.coordination.shared_goal import SharedGoalConsistencyAgent


def test_shared_goal_agent_instantiation():
    agent = SharedGoalConsistencyAgent()
    assert agent is not None


def test_initialize_state_new_startup():
    agent = SharedGoalConsistencyAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        business_name="EcoClean Tech",
        business_idea="AI-driven waterless solar panel cleaning drone system",
        industry="CleanTech",
        target_market="Solar Farm Operators",
        geography="Rajasthan, India",
        primary_goal="Validate market feasibility and financial model",
        budget=1500000.0,
        currency="INR",
        constraints=["Bootstrapped limit 15 Lakhs"],
    )

    state = agent.initialize_state(context)

    # 4. run_id generated
    assert isinstance(state, SharedBusinessState)
    assert state.run_id.startswith("run-")
    # 5 & 6. context and goal preserved
    assert state.business_context.business_name == "EcoClean Tech"
    assert state.business_context.primary_goal == "Validate market feasibility and financial model"
    # 7. constraints preserved
    assert len(state.constraints) == 1
    assert state.constraints[0] == "Bootstrapped limit 15 Lakhs"
    # 10. status is initialized
    assert state.status == StateStatus.INITIALIZED
    # 11, 12, 13. empty conflicts, history, decision
    assert state.conflicts == []
    assert state.negotiation_history == []
    assert state.final_decision is None
    # 8 & 9. facts vs open questions vs assumptions
    facts_text = " ".join(state.canonical_facts)
    assert "EcoClean Tech" in facts_text
    assert "CleanTech" in facts_text
    assert "1,500,000.00 INR" in facts_text


def test_initialize_state_existing_business():
    agent = SharedGoalConsistencyAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_name="Acme Logistics Inc.",
        industry="Logistics",
        primary_goal="Evaluate expansion into cold-chain warehouse automation",
        current_problems=["Rising fuel costs", "Warehouse capacity bottleneck at 82%"],
        existing_metrics={"ARR": "12,000,000 INR"},
    )

    state = agent.initialize_state(context)

    assert isinstance(state, SharedBusinessState)
    assert state.run_id.startswith("run-")
    assert state.status == StateStatus.INITIALIZED
    # Check open questions for missing budget / geography
    open_q_text = " ".join(state.open_questions)
    assert "budget" in open_q_text.lower()
    assert "geographic" in open_q_text.lower()


def test_validate_state_valid():
    agent = SharedGoalConsistencyAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        primary_goal="Test valid state validation",
    )
    state = agent.initialize_state(context)
    is_valid, errors = agent.validate_state(state)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_state_invalid_duplicate_constraints():
    agent = SharedGoalConsistencyAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        primary_goal="Test duplicate constraints",
        constraints=["Max budget limit", "Max budget limit"],  # Duplicate
    )
    state = agent.initialize_state(context)
    is_valid, errors = agent.validate_state(state)
    assert is_valid is False
    assert any("Duplicate constraints" in err for err in errors)


def test_validate_state_missing_goal():
    agent = SharedGoalConsistencyAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        primary_goal="Temporary goal",
    )
    state = agent.initialize_state(context)
    # Manually blank out goal
    state.business_context.primary_goal = "   "
    is_valid, errors = agent.validate_state(state)
    assert is_valid is False
    assert any("primary_goal" in err for err in errors)
