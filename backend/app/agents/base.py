from abc import ABC, abstractmethod
from typing import Dict, List, Any, Union
from pydantic import BaseModel, Field

from app.models.business import BusinessContext
from app.models.agent import AgentPosition


class AgentExecutionContext(BaseModel):
    """
    Execution context wrapper passed to specialist agents during coordination workflows.
    Encapsulates the canonical BusinessContext alongside shared state items like
    verified facts, shared assumptions, active constraints, and previous agent findings.
    """
    business_context: BusinessContext = Field(
        ..., description="The core canonical BusinessContext payload"
    )
    canonical_facts: List[str] = Field(
        default_factory=list, description="Verified cross-domain facts established across execution"
    )
    assumptions: List[str] = Field(
        default_factory=list, description="Global working assumptions established by system or other agents"
    )
    constraints: List[str] = Field(
        default_factory=list, description="Active operational, legal, or strategic constraints"
    )
    previous_findings: Dict[str, Any] = Field(
        default_factory=dict, description="Summary findings or outputs from previously executed agents"
    )


class SpecialistAgent(ABC):
    """
    Abstract Base Class defining the unified contract for all specialist agents in PS-27.
    Enforces a common input parameter model and uniform AgentPosition output format.
    """

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Returns the unique human-readable name of the specialist agent."""
        pass

    @property
    @abstractmethod
    def agent_description(self) -> str:
        """Returns a brief description of the domain perspective evaluated by this agent."""
        pass

    @abstractmethod
    def analyze(
        self, context: Union[BusinessContext, AgentExecutionContext]
    ) -> AgentPosition:
        """
        Executes domain analysis given a BusinessContext or AgentExecutionContext.
        Returns a structured AgentPosition output.
        """
        pass
