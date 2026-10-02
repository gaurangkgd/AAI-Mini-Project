import pytest
from fastapi.testclient import TestClient

from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType, ClaimItem
from app.agents.base import SpecialistAgent, AgentExecutionContext
from app.agents.market_research import MarketResearchAgent
from app.main import app

client = TestClient(app)


def test_agent_instantiation_and_properties():
    agent = MarketResearchAgent()
    assert isinstance(agent, SpecialistAgent)
    assert agent.agent_name == "Market Research Agent"
    assert "market demand" in agent.agent_description.lower()


def test_analyze_new_startup():
    agent = MarketResearchAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        business_name="EcoClean Tech",
        business_idea="AI-driven waterless solar panel cleaning drone system",
        industry="CleanTech",
        target_market="Utility-Scale Solar Farm Operators",
        geography="Rajasthan, India",
        primary_goal="Validate market feasibility and regulatory constraints",
        budget=1500000.0,
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Market Research Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.key_claims) > 0
    for claim in result.key_claims:
        assert isinstance(claim, ClaimItem)
        assert 0.0 <= claim.confidence <= 1.0
    assert result.position == PositionType.CONDITIONAL


def test_analyze_existing_business():
    agent = MarketResearchAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_name="Acme Logistics Inc.",
        industry="Logistics & Freight",
        target_market="B2B E-commerce",
        geography="India",
        primary_goal="Evaluate expansion into cold-chain warehouse automation",
        budget=5000000.0,
        current_problems=["Rising fuel costs"],
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Market Research Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.key_claims) > 0
    assert result.position == PositionType.CONDITIONAL


def test_missing_market_info_handled_gracefully():
    agent = MarketResearchAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        primary_goal="Evaluate vague concept without market parameters",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.position == PositionType.INSUFFICIENT_EVIDENCE
    assert result.confidence <= 0.50
    assert len(result.recommended_actions) > 0
    claims_text = " ".join([c.claim for c in result.key_claims])
    assert "target market" in claims_text.lower() or "industry" in claims_text.lower()


def test_market_research_recommend_stance():
    agent = MarketResearchAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        business_name="RapidGrow SaaS",
        industry="B2B SaaS",
        target_market="Mid-market enterprises",
        geography="North America",
        primary_goal="Scale enterprise tier given high demand and strong tailwinds in market",
        budget=2000000.0,
    )
    result = agent.analyze(context)
    assert result.position == PositionType.RECOMMEND
    assert result.confidence >= 0.80


def test_market_research_do_not_recommend_stance():
    agent = MarketResearchAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_name="Legacy Print",
        industry="Print Publishing",
        target_market="Print Readers",
        geography="Global",
        primary_goal="Expand print distribution in a shrinking market with zero demand",
        budget=500000.0,
    )
    result = agent.analyze(context)
    assert result.position == PositionType.DO_NOT_RECOMMEND
    assert result.confidence >= 0.80


def test_agent_execution_context_wrapper():
    agent = MarketResearchAgent()
    biz_context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        industry="HealthTech",
        target_market="Primary Care Clinics",
        primary_goal="Assess AI diagnostic tool market demand",
    )
    exec_context = AgentExecutionContext(
        business_context=biz_context,
        canonical_facts=["Clinic adoption of digital tools grew post-2020"],
        constraints=["HIPAA compliance mandatory"],
    )

    result = agent.analyze(exec_context)
    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Market Research Agent"
    assert "HIPAA compliance mandatory" in result.constraints_assumed


def test_api_analyze_market_research_endpoint():
    payload = {
        "mode": "new_startup",
        "business_name": "AgriTech Drones",
        "industry": "Agriculture",
        "target_market": "Commercial Wheat Farmers",
        "geography": "Punjab, India",
        "primary_goal": "Assess market adoption of crop monitoring drones",
        "budget": 2500000.0,
    }
    response = client.post("/api/agents/market-research/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_name"] == "Market Research Agent"
    assert "position" in data
    assert "confidence" in data
    assert len(data["key_claims"]) > 0
