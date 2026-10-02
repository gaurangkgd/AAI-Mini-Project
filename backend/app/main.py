from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import settings
from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition
from app.models.state import SharedBusinessState, Conflict, NegotiationRound
from app.agents import (
    MarketResearchAgent,
    FinancialAgent,
    CompetitionAgent,
    CustomerAgent,
    MarketingGTMAgent,
    OperationsAgent,
    RiskRegulatoryAgent,
)
from app.coordination.shared_goal import SharedGoalConsistencyAgent
from app.coordination.conflict_detection import ConflictDetectionAgent
from app.coordination.negotiation import NegotiationAgent
from app.coordination.orchestrator import OrchestratorAgent

app = FastAPI(
    title="Multi-Agent Business & Startup Strategy Advisor",
    description="Collaborative Multi-Agent Coordination System (PS-27)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
    }


@app.post("/api/business/validate", response_model=BusinessContext)
def validate_business_context(context: BusinessContext) -> BusinessContext:
    """
    Validate and normalize a BusinessContext payload for either
    Startup Idea Evaluation or Existing Business Strategic Decision Support.
    """
    return context


@app.get("/api/business/model-example")
def get_model_example(
    mode: Optional[BusinessMode] = Query(
        default=BusinessMode.NEW_STARTUP,
        description="Mode for example data: 'new_startup' or 'existing_business'",
    )
) -> Dict[str, Any]:
    """
    Return an example valid BusinessContext payload based on the requested mode.
    """
    if mode == BusinessMode.EXISTING_BUSINESS:
        example = BusinessContext(
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
    else:
        example = BusinessContext(
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
            existing_metrics={},
            additional_context="Founders have 5 years experience in robotics and power grid operations.",
        )

    return example.model_dump()


@app.post("/api/agents/market-research/analyze", response_model=AgentPosition)
def analyze_market_research(context: BusinessContext) -> AgentPosition:
    """
    Development/testing endpoint for Market Research Agent.
    """
    return MarketResearchAgent().analyze(context)


@app.post("/api/agents/financial/analyze", response_model=AgentPosition)
def analyze_financial(context: BusinessContext) -> AgentPosition:
    """
    Development/testing endpoint for Financial Agent.
    """
    return FinancialAgent().analyze(context)


@app.post("/api/agents/competition/analyze", response_model=AgentPosition)
def analyze_competition(context: BusinessContext) -> AgentPosition:
    """
    Development/testing endpoint for Competition Agent.
    """
    return CompetitionAgent().analyze(context)


@app.post("/api/agents/customer/analyze", response_model=AgentPosition)
def analyze_customer(context: BusinessContext) -> AgentPosition:
    """
    Development/testing endpoint for Customer Agent.
    """
    return CustomerAgent().analyze(context)


@app.post("/api/agents/marketing/analyze", response_model=AgentPosition)
def analyze_marketing(context: BusinessContext) -> AgentPosition:
    """
    Development/testing endpoint for Marketing & GTM Agent.
    """
    return MarketingGTMAgent().analyze(context)


@app.post("/api/agents/operations/analyze", response_model=AgentPosition)
def analyze_operations(context: BusinessContext) -> AgentPosition:
    """
    Development/testing endpoint for Operations Agent.
    """
    return OperationsAgent().analyze(context)


@app.post("/api/agents/risk-regulatory/analyze", response_model=AgentPosition)
def analyze_risk_regulatory(context: BusinessContext) -> AgentPosition:
    """
    Development/testing endpoint for Risk & Regulatory Agent.
    """
    return RiskRegulatoryAgent().analyze(context)


@app.post("/api/coordination/shared-goal/initialize", response_model=SharedBusinessState)
def initialize_shared_goal_state(context: BusinessContext) -> SharedBusinessState:
    """
    Coordination endpoint to initialize and validate canonical SharedBusinessState
    from a BusinessContext input.
    """
    agent = SharedGoalConsistencyAgent()
    state = agent.initialize_state(context)
    is_valid, errors = agent.validate_state(state)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"message": "State validation failed", "errors": errors})
    return state


@app.post("/api/coordination/shared-goal/validate")
def validate_shared_goal_state(state: SharedBusinessState) -> Dict[str, Any]:
    """
    Coordination endpoint to validate an existing SharedBusinessState for consistency.
    """
    agent = SharedGoalConsistencyAgent()
    is_valid, errors = agent.validate_state(state)
    return {
        "valid": is_valid,
        "errors": errors,
        "run_id": state.run_id,
        "status": state.status,
    }


class ConflictDetectionRequest(BaseModel):
    state: SharedBusinessState = Field(..., description="Canonical SharedBusinessState")
    positions: List[AgentPosition] = Field(..., description="List of Specialist Agent positions")


@app.post("/api/coordination/conflicts/detect")
def detect_conflicts(req: ConflictDetectionRequest) -> Dict[str, Any]:
    """
    Coordination endpoint to detect conflicts across specialist agent positions.
    Updates and returns the updated state along with detected conflicts.
    """
    agent = ConflictDetectionAgent()
    conflicts = agent.detect_conflicts(req.state, req.positions)
    return {
        "conflicts": conflicts,
        "count": len(conflicts),
        "status": req.state.status,
        "state": req.state,
    }


class NegotiationRequest(BaseModel):
    state: SharedBusinessState = Field(..., description="Canonical SharedBusinessState")
    positions: List[AgentPosition] = Field(..., description="List of Specialist Agent positions")
    conflicts: List[Conflict] = Field(..., description="List of detected conflicts")


class NegotiationResponse(BaseModel):
    state: SharedBusinessState = Field(..., description="Updated SharedBusinessState with negotiation history and revised positions")
    negotiation_rounds: List[NegotiationRound] = Field(..., description="List of negotiation rounds conducted")
    resolved_conflicts: int = Field(..., description="Count of resolved conflicts")
    unresolved_conflicts: int = Field(..., description="Count of unresolved conflicts")


@app.post("/api/coordination/negotiation/run", response_model=NegotiationResponse)
def run_negotiation(req: NegotiationRequest) -> NegotiationResponse:
    """
    Coordination endpoint to run agent-to-agent negotiation on open conflicts.
    Processes conflicts, records evidence exchange, updates positions, and returns updated state.
    """
    agent = NegotiationAgent()
    updated_state, rounds = agent.run_negotiation(req.state, req.positions, req.conflicts)

    resolved_count = sum(1 for c in req.conflicts if c.status == "resolved")
    unresolved_count = sum(1 for c in req.conflicts if c.status == "unresolved")

    return NegotiationResponse(
        state=updated_state,
        negotiation_rounds=rounds,
        resolved_conflicts=resolved_count,
        unresolved_conflicts=unresolved_count,
    )


@app.post("/api/orchestrate", response_model=SharedBusinessState)
def orchestrate(context: BusinessContext) -> SharedBusinessState:
    """
    End-to-end multi-agent orchestration endpoint.

    Runs the full collaborative pipeline via LangGraph state machine:
      1. Initialize canonical SharedBusinessState (SharedGoal & Consistency Agent)
      2. Run all 7 specialist agents (with per-agent failure isolation)
      3. Detect inter-agent conflicts (first pass)
      4. Conditional: if conflicts → Negotiate → Re-check conflicts (second pass)
      5. Conditional: if significant unresolved → mark HUMAN_REVIEW_REQUIRED
      6. Synthesize FinalDecision from structured state (deterministic rule cascade A–F)

    Input: BusinessContext
    Output: SharedBusinessState with final_decision populated and full collaboration
            trace (agent_positions, conflicts, negotiation_history, revised_positions,
            execution_log).

    Note: confidence in FinalDecision is an aggregate analytical indicator reflecting
    the degree of certainty across the agent collaboration. It does NOT represent a
    probability of business success.
    """
    agent = OrchestratorAgent()
    return agent.run(context)


