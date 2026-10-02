import pytest
from fastapi.testclient import TestClient

from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType
from app.agents.base import SpecialistAgent, AgentExecutionContext
from app.agents.marketing import MarketingGTMAgent
from app.main import app

client = TestClient(app)


def test_marketing_agent_properties():
    agent = MarketingGTMAgent()
    assert isinstance(agent, SpecialistAgent)
    assert agent.agent_name == "Marketing & GTM Agent"
    assert "positioning" in agent.agent_description.lower() or "market" in agent.agent_description.lower()


def test_marketing_analyze_startup():
    agent = MarketingGTMAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        target_market="Solar Operators",
        business_model="RaaS Subscription",
        geography="Rajasthan",
        primary_goal="Validate GTM channels",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Marketing & GTM Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.key_claims) > 0
    assert result.position == PositionType.CONDITIONAL


def test_marketing_analyze_existing():
    agent = MarketingGTMAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        target_market="Manufacturing B2B",
        geography="India",
        primary_goal="Expand GTM reach",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Marketing & GTM Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert result.position == PositionType.CONDITIONAL


def test_marketing_missing_target_market():
    agent = MarketingGTMAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        primary_goal="GTM without target segment",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.position == PositionType.INSUFFICIENT_EVIDENCE


def test_marketing_recommend_on_strong_organic_viral_channel():
    agent = MarketingGTMAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        target_market="College Students",
        business_model="Freemium",
        geography="India",
        primary_goal="Scale platform through built-in viral referral and strong organic growth with low CAC",
    )
    result = agent.analyze(context)
    assert result.position == PositionType.RECOMMEND
    assert result.confidence >= 0.80


def test_marketing_do_not_recommend_on_growth_spend_mismatch():
    agent = MarketingGTMAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        target_market="College Students",
        geography="India",
        primary_goal="Achieve 3x user growth within 6 months",
        constraints=[
            "Cannot significantly increase marketing spending",
            "Current customer acquisition cost is already high",
        ],
    )
    result = agent.analyze(context)
    assert result.position == PositionType.DO_NOT_RECOMMEND
    assert result.confidence >= 0.80


def test_marketing_api_endpoint():
    payload = {
        "mode": "new_startup",
        "target_market": "B2B SaaS",
        "primary_goal": "Assess marketing strategy",
    }
    response = client.post("/api/agents/marketing/analyze", json=payload)
    assert response.status_code == 200
    assert response.json()["agent_name"] == "Marketing & GTM Agent"
