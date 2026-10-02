import pytest
from fastapi.testclient import TestClient

from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType
from app.agents.base import SpecialistAgent, AgentExecutionContext
from app.agents.operations import OperationsAgent
from app.main import app

client = TestClient(app)


def test_operations_agent_properties():
    agent = OperationsAgent()
    assert isinstance(agent, SpecialistAgent)
    assert agent.agent_name == "Operations Agent"
    assert "operational" in agent.agent_description.lower() or "execution" in agent.agent_description.lower()


def test_operations_analyze_startup():
    agent = OperationsAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        business_stage="Pre-seed",
        time_horizon="6 months",
        constraints=["Bootstrapped limit"],
        primary_goal="Assess launch execution",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Operations Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.key_claims) > 0
    assert result.position == PositionType.CONDITIONAL


def test_operations_analyze_existing():
    agent = OperationsAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_stage="Growth",
        current_problems=["Warehouse capacity bottleneck at 82%"],
        primary_goal="Expand warehouse automation",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Operations Agent"
    assert 0.0 <= result.confidence <= 1.0
    claims_text = " ".join([c.claim for c in result.key_claims])
    assert "bottlenecks" in claims_text.lower() or "capacity" in claims_text.lower()
    assert result.position == PositionType.CONDITIONAL


def test_operations_missing_context():
    agent = OperationsAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        primary_goal="",
    )
    result = agent.analyze(context)
    assert result.position == PositionType.INSUFFICIENT_EVIDENCE


def test_operations_recommend_on_scalable_automation():
    agent = OperationsAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        business_stage="MVP",
        time_horizon="6 months",
        primary_goal="Scale digital platform with cloud-native auto-scales server architecture and fully automated SOPs",
    )
    result = agent.analyze(context)
    assert result.position == PositionType.RECOMMEND
    assert result.confidence >= 0.80


def test_operations_do_not_recommend_on_infrastructure_breakdown():
    agent = OperationsAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_stage="Growth",
        time_horizon="1 month",
        primary_goal="Triple production output despite supply chain breakdown and infrastructure cannot scale",
    )
    result = agent.analyze(context)
    assert result.position == PositionType.DO_NOT_RECOMMEND
    assert result.confidence >= 0.80


def test_operations_api_endpoint():
    payload = {
        "mode": "existing_business",
        "primary_goal": "Assess ops bottlenecks",
        "current_problems": ["Fleet fuel cost rising"],
    }
    response = client.post("/api/agents/operations/analyze", json=payload)
    assert response.status_code == 200
    assert response.json()["agent_name"] == "Operations Agent"
