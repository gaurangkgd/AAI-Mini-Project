from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.business import BusinessContext
from app.models.agent import AgentPosition, PositionType, AgentExecutionRecord


class ConflictType(str, Enum):
    """Categorization of agent disagreements."""
    POSITION_CONFLICT = "position_conflict"
    ASSUMPTION_CONFLICT = "assumption_conflict"
    CONSTRAINT_CONFLICT = "constraint_conflict"
    EVIDENCE_CONFLICT = "evidence_conflict"
    PRIORITY_CONFLICT = "priority_conflict"


class ConflictStatus(str, Enum):
    """Lifecycle status of a detected conflict."""
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    ESCALATED = "escalated"


class Conflict(BaseModel):
    """
    Representation of an explicit disagreement detected between two or more agents.
    """
    conflict_id: str = Field(..., description="Unique identifier for the conflict")
    agents_involved: List[str] = Field(..., description="List of agent names involved in the disagreement")
    conflict_type: ConflictType = Field(..., description="Category of the conflict")
    description: str = Field(..., description="Detailed description of the disagreement")
    conflicting_claims: List[str] = Field(default_factory=list, description="Specific claims in opposition")
    conflicting_assumptions: List[str] = Field(default_factory=list, description="Contradictory assumptions identified")
    severity: str = Field(default="medium", description="Severity level (e.g., 'low', 'medium', 'high', 'critical')")
    status: ConflictStatus = Field(default=ConflictStatus.OPEN, description="Current resolution status")
    resolution: Optional[str] = Field(default=None, description="Summary of how the conflict was resolved")
    supporting_evidence: List[str] = Field(default_factory=list, description="Evidence used during conflict evaluation")


class NegotiationRound(BaseModel):
    """
    Record of a single negotiation round between conflicting agents.
    Preserves history of how agents adapted their positions over time.
    """
    round_number: int = Field(..., ge=1, description="Sequential round number of negotiation")
    participants: List[str] = Field(..., description="Agents participating in this round")
    issue: str = Field(..., description="The core issue or conflict being negotiated")
    previous_positions: List[AgentPosition] = Field(default_factory=list, description="Agent positions prior to round")
    evidence_exchanged: List[str] = Field(default_factory=list, description="New evidence introduced during round")
    arguments: List[str] = Field(default_factory=list, description="Counterarguments presented by agents")
    revised_positions: List[AgentPosition] = Field(default_factory=list, description="Updated agent positions post-round")
    resolution: Optional[str] = Field(default=None, description="Resolution achieved in this round, if any")
    unresolved_points: List[str] = Field(default_factory=list, description="Points that remain contentious")


class FinalDecision(BaseModel):
    """
    Synthesized final decision produced by Orchestrator / Synthesis Agent.
    """
    recommendation: PositionType = Field(..., description="Final strategic recommendation")
    rationale: str = Field(..., description="Comprehensive executive summary and justification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score in final decision (0.0 to 1.0)")
    key_factors: List[str] = Field(default_factory=list, description="Primary drivers influencing the recommendation")
    alternatives_considered: List[str] = Field(default_factory=list, description="Alternative strategic paths evaluated")
    trade_offs: List[str] = Field(default_factory=list, description="Key strategic or financial trade-offs accepted")
    risks: List[str] = Field(default_factory=list, description="Critical risks and mitigation strategies")
    assumptions: List[str] = Field(default_factory=list, description="Core assumptions underlying the final decision")
    unresolved_dissent: List[str] = Field(default_factory=list, description="Preserved minority agent dissent or concerns")
    action_plan: List[str] = Field(default_factory=list, description="Sequential action items for execution")
    evidence_trace: List[str] = Field(default_factory=list, description="Traceability links to supporting agent evidence")


class StateStatus(str, Enum):
    """Overall execution status of the shared business state."""
    INITIALIZED = "initialized"
    ANALYZING = "analyzing"
    CONFLICT_DETECTED = "conflict_detected"
    NEGOTIATING = "negotiating"
    CONSENSUS_REACHED = "consensus_reached"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    COMPLETED = "completed"


class SharedBusinessState(BaseModel):
    """
    Central canonical state passed through the multi-agent coordination workflow (e.g., LangGraph).
    Serves as the single source of truth across all 10 agents.
    """
    run_id: str = Field(..., description="Unique execution or session identifier")
    business_context: BusinessContext = Field(..., description="Initial input business parameters")
    canonical_facts: List[str] = Field(default_factory=list, description="Verified facts established across agents")
    constraints: List[str] = Field(default_factory=list, description="Active business and operational constraints")
    assumptions: List[str] = Field(default_factory=list, description="Global and agent-specific working assumptions")
    open_questions: List[str] = Field(default_factory=list, description="Unresolved questions requiring further data")
    agent_positions: List[AgentPosition] = Field(default_factory=list, description="Initial positions returned by agents (originals, never overwritten)")
    conflicts: List[Conflict] = Field(default_factory=list, description="Active or historical conflicts detected")
    negotiation_history: List[NegotiationRound] = Field(default_factory=list, description="Log of negotiation iterations")
    revised_positions: List[AgentPosition] = Field(default_factory=list, description="Latest revised agent positions post-negotiation")
    final_decision: Optional[FinalDecision] = Field(default=None, description="Final synthesized decision output")
    status: StateStatus = Field(default=StateStatus.INITIALIZED, description="Current workflow state")
    execution_log: List[AgentExecutionRecord] = Field(
        default_factory=list,
        description="Per-agent success/failure record from the orchestration run"
    )
