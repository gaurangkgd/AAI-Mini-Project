from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BusinessMode(str, Enum):
    """Supported operation modes for business analysis."""
    NEW_STARTUP = "new_startup"
    EXISTING_BUSINESS = "existing_business"


class BusinessContext(BaseModel):
    """
    Canonical business context model representing input parameters
    for both Startup Idea Evaluation and Existing Business Strategic Decision Support.
    """
    mode: BusinessMode = Field(
        ...,
        description="Mode of operation: 'new_startup' or 'existing_business'",
    )
    business_name: Optional[str] = Field(
        default=None, description="Name of the business or venture"
    )
    business_idea: Optional[str] = Field(
        default=None, description="Core business concept or value proposition"
    )
    business_description: Optional[str] = Field(
        default=None, description="Detailed overview of operations or offering"
    )
    industry: Optional[str] = Field(
        default=None, description="Industry sector (e.g., FinTech, SaaS, Healthcare)"
    )
    target_market: Optional[str] = Field(
        default=None, description="Target customer segment or demographic"
    )
    geography: Optional[str] = Field(
        default=None, description="Target geographic region or market"
    )
    business_model: Optional[str] = Field(
        default=None, description="Monetization approach (e.g., B2B SaaS, Marketplace)"
    )
    business_stage: Optional[str] = Field(
        default=None, description="Current stage (e.g., Idea, MVP, Seed, Growth)"
    )
    primary_goal: str = Field(
        ..., description="Primary strategic objective or question to evaluate"
    )
    budget: Optional[float] = Field(
        default=None, ge=0.0, description="Available budget for execution/investigation"
    )
    currency: str = Field(
        default="INR", description="Currency code for monetary metrics"
    )
    time_horizon: Optional[str] = Field(
        default=None, description="Execution/evaluation timeline (e.g., 6 months, 3 years)"
    )
    constraints: List[str] = Field(
        default_factory=list, description="Known operational, legal, or financial constraints"
    )
    current_problems: List[str] = Field(
        default_factory=list, description="Pain points or key bottlenecks facing the business"
    )
    existing_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Current metrics (e.g., ARR, CAC, LTV, churn)"
    )
    additional_context: Optional[str] = Field(
        default=None, description="Any additional qualitative context or notes"
    )
