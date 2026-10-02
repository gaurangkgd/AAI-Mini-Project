import pytest
from fastapi.testclient import TestClient

from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType
from app.agents.base import SpecialistAgent, AgentExecutionContext
from app.agents.customer import CustomerAgent
from app.main import app

client = TestClient(app)


def test_customer_agent_properties():
    agent = CustomerAgent()
    assert isinstance(agent, SpecialistAgent)
    assert agent.agent_name == "Customer Agent"
    assert "customer" in agent.agent_description.lower()


def test_customer_analyze_startup():
    agent = CustomerAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        target_market="Utility Solar Farm Operators",
        primary_goal="Assess buyer pain points",
        current_problems=["High manual cleaning cost"],
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Customer Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.key_claims) > 0
    assert result.position == PositionType.CONDITIONAL


def test_customer_analyze_existing():
    agent = CustomerAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        target_market="Enterprise Fleet Managers",
        primary_goal="Improve customer retention",
        existing_metrics={"churn": "3.5%"},
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Customer Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert result.position == PositionType.CONDITIONAL


def test_customer_missing_target_market():
    agent = CustomerAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        primary_goal="Undefined customer segment",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.position == PositionType.INSUFFICIENT_EVIDENCE


def test_customer_recommend_on_student_price_reduction_fit():
    agent = CustomerAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_name="QuickLearn",
        target_market="College students aged 18-24 across India",
        primary_goal="Reduce subscription price by 50% to rapidly increase student users",
    )
    result = agent.analyze(context)
    assert result.position == PositionType.RECOMMEND
    assert result.confidence >= 0.80


def test_customer_do_not_recommend_on_severe_churn():
    agent = CustomerAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_name="Failing App",
        target_market="Enterprise Consumers",
        primary_goal="Expand marketing despite severe churn, declining NPS, and customers rejecting product",
    )
    result = agent.analyze(context)
    assert result.position == PositionType.DO_NOT_RECOMMEND
    assert result.confidence >= 0.80


def test_customer_api_endpoint():
    payload = {
        "mode": "new_startup",
        "target_market": "Primary Care Clinics",
        "primary_goal": "Assess customer fit",
    }
    response = client.post("/api/agents/customer/analyze", json=payload)
    assert response.status_code == 200
    assert response.json()["agent_name"] == "Customer Agent"
