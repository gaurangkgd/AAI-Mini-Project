import pytest
from fastapi.testclient import TestClient

from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType, ClaimItem
from app.agents.base import SpecialistAgent, AgentExecutionContext
from app.agents.financial import FinancialAgent
from app.main import app

client = TestClient(app)


def test_financial_agent_instantiation_and_properties():
    agent = FinancialAgent()
    assert isinstance(agent, SpecialistAgent)
    assert agent.agent_name == "Financial Agent"
    assert "budget" in agent.agent_description.lower() or "financial" in agent.agent_description.lower()


def test_financial_analyze_new_startup():
    agent = FinancialAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        business_name="EcoClean Tech",
        primary_goal="Validate financial model",
        budget=1500000.0,
        currency="INR",
        time_horizon="6 months",
        business_model="Subscription RaaS",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Financial Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.key_claims) > 0
    assert result.position == PositionType.CONDITIONAL


def test_financial_analyze_existing_business():
    agent = FinancialAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_name="Acme Logistics Inc.",
        primary_goal="Cold chain warehouse expansion",
        budget=5000000.0,
        currency="INR",
        existing_metrics={"ARR": "12,000,000 INR"},
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Financial Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.key_claims) > 0
    assert result.position == PositionType.CONDITIONAL


def test_financial_missing_budget():
    agent = FinancialAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        primary_goal="Assess unbudgeted venture",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.position == PositionType.INSUFFICIENT_EVIDENCE
    assert result.confidence <= 0.50


def test_financial_do_not_recommend_on_severe_cash_tension():
    agent = FinancialAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_name="QuickLearn",
        primary_goal="Reduce subscription price by 50% while maintaining positive cash flow",
        budget=500000.0,
        currency="INR",
        time_horizon="6 months",
        constraints=[
            "Limited cash reserves",
            "Cannot significantly increase marketing spending",
            "Current customer acquisition cost is already high",
        ],
    )
    result = agent.analyze(context)
    assert result.position == PositionType.DO_NOT_RECOMMEND
    assert result.confidence >= 0.80
    claims_text = " ".join([c.claim for c in result.key_claims]).lower()
    assert "cash-flow" in claims_text or "unit revenue" in claims_text or "cash" in claims_text


def test_financial_recommend_on_strong_capital_health():
    agent = FinancialAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_name="Profitable SaaS",
        primary_goal="Expand sales tier with strong cash reserves and positive EBITDA",
        budget=10000000.0,
        currency="INR",
        time_horizon="12 months",
        business_model="B2B SaaS",
    )
    result = agent.analyze(context)
    assert result.position == PositionType.RECOMMEND
    assert result.confidence >= 0.80


def test_financial_agent_execution_context():
    agent = FinancialAgent()
    biz_ctx = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        budget=500000.0,
        primary_goal="Test execution wrapper",
    )
    exec_ctx = AgentExecutionContext(business_context=biz_ctx)
    result = agent.analyze(exec_ctx)
    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Financial Agent"


def test_financial_api_endpoint():
    payload = {
        "mode": "new_startup",
        "primary_goal": "Financial test",
        "budget": 1000000.0,
    }
    response = client.post("/api/agents/financial/analyze", json=payload)
    assert response.status_code == 200
    assert response.json()["agent_name"] == "Financial Agent"
