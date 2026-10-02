import pytest
from fastapi.testclient import TestClient

from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType
from app.agents.base import SpecialistAgent, AgentExecutionContext
from app.agents.competition import CompetitionAgent
from app.main import app

client = TestClient(app)


def test_competition_agent_properties():
    agent = CompetitionAgent()
    assert isinstance(agent, SpecialistAgent)
    assert agent.agent_name == "Competition Agent"
    assert "competitive" in agent.agent_description.lower()


def test_competition_analyze_startup():
    agent = CompetitionAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        industry="SaaS",
        target_market="SMB Retailers",
        primary_goal="Assess competitive differentiation",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Competition Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.key_claims) > 0
    assert result.position == PositionType.CONDITIONAL


def test_competition_analyze_existing():
    agent = CompetitionAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        industry="Logistics",
        primary_goal="Defend market share",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Competition Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert result.position == PositionType.CONDITIONAL


def test_competition_missing_industry():
    agent = CompetitionAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        primary_goal="Vague goal without industry",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.position == PositionType.INSUFFICIENT_EVIDENCE
    assert result.confidence <= 0.50


def test_competition_recommend_on_strong_moat():
    agent = CompetitionAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        industry="MedTech",
        target_market="Hospitals",
        business_idea="Proprietary patented AI imaging hardware with high switching costs and exclusive partnership",
        primary_goal="Enter surgical imaging market",
    )
    result = agent.analyze(context)
    assert result.position == PositionType.RECOMMEND
    assert result.confidence >= 0.80


def test_competition_do_not_recommend_on_severe_commoditization():
    agent = CompetitionAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        industry="RideSharing",
        target_market="Commuters",
        primary_goal="Launch in market dominated by monopoly incumbent in a fierce price war with commoditized offering and no differentiation",
    )
    result = agent.analyze(context)
    assert result.position == PositionType.DO_NOT_RECOMMEND
    assert result.confidence >= 0.80


def test_competition_api_endpoint():
    payload = {
        "mode": "new_startup",
        "industry": "CleanTech",
        "primary_goal": "Assess competitors",
    }
    response = client.post("/api/agents/competition/analyze", json=payload)
    assert response.status_code == 200
    assert response.json()["agent_name"] == "Competition Agent"
