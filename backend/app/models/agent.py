from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class PositionType(str, Enum):
    """Possible strategic positions a specialist agent can adopt."""
    RECOMMEND = "recommend"
    DO_NOT_RECOMMEND = "do_not_recommend"
    CONDITIONAL = "conditional"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class ClaimItem(BaseModel):
    """Structured individual claim or assertion made by an agent."""
    claim: str = Field(..., description="The core assertion made by the agent")
    evidence: Optional[str] = Field(default=None, description="Supporting evidence for the claim")
    source: Optional[str] = Field(default=None, description="Data source or reference")
    assumption: Optional[str] = Field(default=None, description="Underlying assumption supporting the claim")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this specific claim (0.0 to 1.0)")


class AgentPosition(BaseModel):
    """
    Structured position output returned by each specialist agent.
    Serves as the canonical output data contract across all specialist agents.
    """
    agent_name: str = Field(..., description="Identifier of the specialist agent (e.g., 'Financial Agent')")
    position: PositionType = Field(..., description="Overall strategic stance or recommendation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall position confidence score (0.0 to 1.0)")
    key_claims: List[ClaimItem] = Field(default_factory=list, description="Structured claims supporting the position")
    evidence: List[str] = Field(default_factory=list, description="Factual evidence items")
    assumptions: List[str] = Field(default_factory=list, description="Key assumptions relied upon")
    constraints_assumed: List[str] = Field(default_factory=list, description="Constraints factored into the analysis")
    risks: List[str] = Field(default_factory=list, description="Identified risks from the agent's domain perspective")
    recommended_actions: List[str] = Field(default_factory=list, description="Concrete recommended next steps")


class AgentExecutionRecord(BaseModel):
    """
    Records the outcome of a single specialist agent execution during orchestration.
    Tracks success/failure without fabricating positions on failure.
    """
    agent_name: str = Field(..., description="Name of the specialist agent")
    success: bool = Field(..., description="True if the agent completed execution without error")
    position: Optional[AgentPosition] = Field(
        default=None,
        description="Agent's returned position (populated only on success)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if the agent failed (populated only on failure)"
    )
