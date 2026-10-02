import pytest
from fastapi.testclient import TestClient

from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType
from app.agents.base import SpecialistAgent, AgentExecutionContext
from app.agents.risk_regulatory import RiskRegulatoryAgent
from app.main import app

client = TestClient(app)


def test_risk_regulatory_agent_properties():
    agent = RiskRegulatoryAgent()
    assert isinstance(agent, SpecialistAgent)
    assert agent.agent_name == "Risk & Regulatory Agent"
    assert "regulatory" in agent.agent_description.lower() or "risk" in agent.agent_description.lower()


def test_risk_regulatory_analyze_startup():
    agent = RiskRegulatoryAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        industry="CleanTech",
        geography="Rajasthan, India",
        constraints=["Comply with DGCA drone regulations"],
        primary_goal="Evaluate regulatory risk",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Risk & Regulatory Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.key_claims) > 0
    assumptions_text = " ".join(result.assumptions)
    assert "DOES NOT CONSTITUTE FORMAL LEGAL ADVICE" in assumptions_text
    assert result.position == PositionType.CONDITIONAL


def test_risk_regulatory_analyze_existing():
    agent = RiskRegulatoryAgent()
    context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        industry="Logistics",
        geography="India",
        constraints=["Regulatory approval required for cold storage"],
        primary_goal="Cold storage expansion legal audit",
    )
    result = agent.analyze(context)

    assert isinstance(result, AgentPosition)
    assert result.agent_name == "Risk & Regulatory Agent"
    assert 0.0 <= result.confidence <= 1.0
    assert result.position == PositionType.CONDITIONAL


def test_risk_regulatory_missing_context():
    agent = RiskRegulatoryAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        primary_goal="",
    )
    result = agent.analyze(context)
    assert result.position == PositionType.INSUFFICIENT_EVIDENCE


def test_risk_regulatory_recommend_on_low_risk_compliance():
    agent = RiskRegulatoryAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        industry="EdTech",
        geography="India",
        primary_goal="Launch standard digital learning app which is fully licensed and compliant with no special regulatory licensing required",
    )
    result = agent.analyze(context)
    assert result.position == PositionType.RECOMMEND
    assert result.confidence >= 0.80


def test_risk_regulatory_do_not_recommend_on_regulatory_ban():
    agent = RiskRegulatoryAgent()
    context = BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        industry="CryptoGambling",
        geography="India",
        primary_goal="Launch platform under active regulatory ban and illegal statutory prohibition",
    )
    result = agent.analyze(context)
    assert result.position == PositionType.DO_NOT_RECOMMEND
    assert result.confidence >= 0.80


def test_risk_regulatory_api_endpoint():
    payload = {
        "mode": "new_startup",
        "industry": "HealthTech",
        "geography": "India",
        "primary_goal": "Assess HIPAA/DISHA compliance risk",
    }
    response = client.post("/api/agents/risk-regulatory/analyze", json=payload)
    assert response.status_code == 200
    assert response.json()["agent_name"] == "Risk & Regulatory Agent"
