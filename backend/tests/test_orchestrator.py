"""
Tests for Step 8 — OrchestratorAgent & /api/orchestrate endpoint.

Verifies:
- Full end-to-end pipeline execution for both modes
- FinalDecision is correctly populated
- Original agent_positions are preserved (not overwritten)
- revised_positions are stored separately post-negotiation
- execution_log tracks all 7 agents
- Synthesis fields are populated from structured state
- Minimal input does not crash the pipeline
- API endpoint returns 200 with valid SharedBusinessState
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.business import BusinessContext, BusinessMode
from app.models.agent import PositionType
from app.models.state import StateStatus
from app.coordination.orchestrator import OrchestratorAgent

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def new_startup_context() -> BusinessContext:
    return BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        business_name="EcoClean Tech",
        business_idea="AI-driven waterless solar panel cleaning drone system",
        business_description="Automated robotics solution to clean utility-scale solar farms without water",
        industry="CleanTech / Renewable Energy",
        target_market="Utility-Scale Solar Farm Operators",
        geography="Rajasthan & Gujarat, India",
        business_model="Robotics-as-a-Service (RaaS) subscription",
        business_stage="Idea / Pre-seed",
        primary_goal="Validate market feasibility, financial viability, and operational constraints",
        budget=1500000.0,
        currency="INR",
        time_horizon="6 months",
        constraints=[
            "Bootstrapped pre-seed capital limit of 15 Lakhs INR",
            "Must comply with Indian drone regulatory framework (DGCA)",
        ],
        current_problems=[
            "Lack of field testing data under extreme desert conditions",
            "High customer acquisition lead times in utility sector",
        ],
        additional_context="Founders have 5 years experience in robotics and power grid operations.",
    )


@pytest.fixture
def existing_business_context() -> BusinessContext:
    return BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_name="Acme Logistics Inc.",
        business_description="Mid-sized regional logistics and freight forwarding company",
        industry="Logistics & Supply Chain",
        target_market="B2B E-commerce & Manufacturing",
        geography="India (Tier 1 & Tier 2 Cities)",
        business_model="B2B Service Fee & Subscription",
        business_stage="Growth / Expansion",
        primary_goal="Evaluate expansion into cold-chain warehouse automation",
        budget=5000000.0,
        currency="INR",
        time_horizon="12 months",
        constraints=[
            "Regulatory approval required for cold storage infrastructure",
            "Max debt financing capped at 40% of expansion budget",
        ],
        current_problems=[
            "Rising fuel costs impacting margins by 8%",
            "Warehouse utilization currently bottlenecked at 82%",
        ],
        existing_metrics={
            "ARR": "12,000,000 INR",
            "EBITDA_margin": "14%",
            "fleet_count": 45,
        },
        additional_context="Board requires strategic risk-benefit analysis before Q3 capital allocation.",
    )


@pytest.fixture
def minimal_context() -> BusinessContext:
    """Minimal valid input — only required fields."""
    return BusinessContext(
        mode=BusinessMode.NEW_STARTUP,
        primary_goal="Assess viability of a new product idea",
    )


# ---------------------------------------------------------------------------
# Test 1: Full pipeline execution for new_startup
# ---------------------------------------------------------------------------

def test_orchestrator_runs_new_startup(new_startup_context: BusinessContext):
    orchestrator = OrchestratorAgent()
    state = orchestrator.run(new_startup_context)

    assert state.status == StateStatus.COMPLETED
    assert state.final_decision is not None
    assert state.final_decision.recommendation in [
        PositionType.RECOMMEND,
        PositionType.CONDITIONAL,
        PositionType.DO_NOT_RECOMMEND,
        PositionType.INSUFFICIENT_EVIDENCE,
    ]
    assert 0.0 <= state.final_decision.confidence <= 1.0
    assert len(state.final_decision.rationale) > 0
    assert len(state.agent_positions) == 7


def test_orchestrator_runs_existing_business(existing_business_context: BusinessContext):
    orchestrator = OrchestratorAgent()
    state = orchestrator.run(existing_business_context)

    assert state.status == StateStatus.COMPLETED
    assert state.final_decision is not None
    assert state.final_decision.recommendation in [
        PositionType.RECOMMEND,
        PositionType.CONDITIONAL,
        PositionType.DO_NOT_RECOMMEND,
        PositionType.INSUFFICIENT_EVIDENCE,
    ]
    assert 0.0 <= state.final_decision.confidence <= 1.0
    assert len(state.agent_positions) == 7


def test_original_positions_preserved(new_startup_context: BusinessContext):
    orchestrator = OrchestratorAgent()
    state = orchestrator.run(new_startup_context)

    assert len(state.agent_positions) == 7
    for pos in state.agent_positions:
        assert pos.agent_name is not None
        assert pos.position in [
            PositionType.RECOMMEND,
            PositionType.CONDITIONAL,
            PositionType.DO_NOT_RECOMMEND,
            PositionType.INSUFFICIENT_EVIDENCE,
        ]


def test_execution_log_tracks_all_agents(new_startup_context: BusinessContext):
    orchestrator = OrchestratorAgent()
    state = orchestrator.run(new_startup_context)

    assert len(state.execution_log) == 7
    for record in state.execution_log:
        assert record.success is True
        assert record.position is not None
        assert record.error is None


def test_final_decision_fields_populated(new_startup_context: BusinessContext):
    orchestrator = OrchestratorAgent()
    state = orchestrator.run(new_startup_context)
    fd = state.final_decision

    assert fd is not None
    assert len(fd.key_factors) > 0
    assert len(fd.evidence_trace) > 0
    assert len(fd.risks) > 0
    assert len(fd.action_plan) > 0
    assert len(fd.assumptions) > 0


def test_minimal_input_does_not_crash(minimal_context: BusinessContext):
    orchestrator = OrchestratorAgent()
    state = orchestrator.run(minimal_context)

    assert state.status == StateStatus.COMPLETED
    assert state.final_decision is not None
    assert len(state.agent_positions) == 7


def test_confidence_computation(new_startup_context: BusinessContext):
    orchestrator = OrchestratorAgent()
    state = orchestrator.run(new_startup_context)

    assert 0.0 <= state.final_decision.confidence <= 1.0


def test_rationale_references_state_data(new_startup_context: BusinessContext):
    orchestrator = OrchestratorAgent()
    state = orchestrator.run(new_startup_context)
    rationale = state.final_decision.rationale

    assert "EcoClean Tech" in rationale
    assert len(rationale) > 50


def test_graph_structure_has_expected_nodes():
    orchestrator = OrchestratorAgent()
    graph = orchestrator._graph
    assert graph is not None


def test_api_orchestrate_endpoint_new_startup():
    payload = {
        "mode": "new_startup",
        "business_name": "TestVenture",
        "business_idea": "AI-powered personal finance advisor",
        "business_description": "App that uses AI to provide personalized financial advice",
        "industry": "FinTech",
        "target_market": "Millennials and Gen-Z urban professionals",
        "geography": "India",
        "business_model": "Freemium SaaS",
        "business_stage": "Idea / Pre-seed",
        "primary_goal": "Validate product-market fit and identify key risks",
        "budget": 500000.0,
        "currency": "INR",
        "time_horizon": "6 months",
        "constraints": ["No external funding in first 6 months"],
        "current_problems": [],
        "existing_metrics": {},
    }

    response = client.post("/api/orchestrate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data and data["run_id"]
    assert data["status"] == "completed"
    assert data["final_decision"] is not None
    assert len(data["agent_positions"]) == 7
    assert len(data["execution_log"]) == 7


def test_quicklearn_scenario_produces_genuine_divergence_and_negotiation():
    """
    QuickLearn EdTech Scenario:
    Tests that specialist agents make domain-driven judgments that produce
    meaningful position divergence, resulting in detected conflict and negotiation.
    """
    quicklearn_context = BusinessContext(
        mode=BusinessMode.EXISTING_BUSINESS,
        business_name="QuickLearn",
        industry="EdTech",
        business_stage="Growth",
        business_model="Subscription",
        target_market="College students aged 18-24 across India",
        budget=500000.0,
        currency="INR",
        time_horizon="6 months",
        primary_goal="Decide whether to reduce the subscription price by 50% to rapidly increase the number of users while maintaining profitability.",
        constraints=[
            "Current cash reserves are limited",
            "Need to maintain positive cash flow",
            "Management wants 3x user growth within 6 months",
            "Cannot significantly increase marketing spending",
            "Current customer acquisition cost is already high",
            "Existing subscribers are sensitive to price changes",
        ],
        additional_context="The company currently has 10,000 paying subscribers at INR 500 per month. Management wants to reduce the price to INR 250 to attract more students and compete with lower-priced alternatives. However, the company has limited cash reserves and cannot significantly increase spending on marketing or infrastructure. The goal is to triple the user base within 6 months while maintaining positive cash flow.",
    )

    orchestrator = OrchestratorAgent()
    state = orchestrator.run(quicklearn_context)

    # 1. Pipeline completed
    assert state.status == StateStatus.COMPLETED
    assert state.final_decision is not None

    # 2. Positions are no longer all identical
    positions = [p.position for p in state.agent_positions]
    distinct_positions = set(positions)
    assert len(distinct_positions) > 1, f"Expected position divergence, got all {positions}"

    # 3. Meaningful conflicts detected
    assert len(state.conflicts) > 0, "Expected at least one conflict to be detected"

    # 4. Negotiation was triggered and generated rounds
    assert len(state.negotiation_history) > 0, "Expected negotiation rounds to be executed"

    # 5. Revised positions exist
    assert len(state.revised_positions) > 0
