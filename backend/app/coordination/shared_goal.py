import uuid
from typing import Tuple, List
from app.models.business import BusinessContext, BusinessMode
from app.models.state import SharedBusinessState, StateStatus


class SharedGoalConsistencyAgent:
    """
    Shared Goal & Consistency Coordination Agent.
    Maintains a canonical, normalized interpretation of the business decision state
    that all 7 specialist agents rely upon.
    """

    def initialize_state(self, context: BusinessContext) -> SharedBusinessState:
        """
        Initializes a new SharedBusinessState from a BusinessContext payload.
        Extracts canonical facts, preserves constraints, identifies assumptions vs open questions,
        and generates a unique run_id.
        """
        run_id = f"run-{uuid.uuid4().hex[:12]}"

        canonical_facts = []
        assumptions = []
        open_questions = []
        constraints = list(context.constraints)

        # 1. Primary Goal Facts
        canonical_facts.append(f"Primary Decision Objective: '{context.primary_goal}'.")

        # 2. Mode & Business Name
        if context.business_name:
            canonical_facts.append(f"Venture Name: '{context.business_name}'.")

        if context.mode == BusinessMode.NEW_STARTUP:
            canonical_facts.append("Operating Mode: Startup Idea Evaluation.")
            if context.business_idea:
                canonical_facts.append(f"Core Business Concept: '{context.business_idea}'.")
            if context.business_stage:
                canonical_facts.append(f"Venture Stage: '{context.business_stage}'.")
            else:
                assumptions.append("Venture stage assumed to be Early Idea / Pre-seed stage.")

        else:  # EXISTING_BUSINESS
            canonical_facts.append("Operating Mode: Existing Business Strategic Decision Support.")
            if context.business_stage:
                canonical_facts.append(f"Operating Stage: '{context.business_stage}'.")

            if context.current_problems:
                canonical_facts.append(
                    f"Reported Operational/Business Problems: {', '.join(context.current_problems)}."
                )

            if context.existing_metrics:
                metrics_str = ", ".join([f"{k}: {v}" for k, v in context.existing_metrics.items()])
                canonical_facts.append(f"Reported Operating Metrics: {metrics_str}.")

        # 3. Industry & Geography Facts vs Open Questions
        if context.industry:
            canonical_facts.append(f"Industry Classification: '{context.industry}'.")
        else:
            open_questions.append("Industry sector is unclassified.")

        if context.target_market:
            canonical_facts.append(f"Target Customer Segment: '{context.target_market}'.")
        else:
            open_questions.append("Target customer market demographic is unspecified.")

        if context.geography:
            canonical_facts.append(f"Target Geographic Footprint: '{context.geography}'.")
        else:
            open_questions.append("Target geographic region is unspecified.")

        # 4. Budget & Currency
        if context.budget is not None and context.budget > 0:
            canonical_facts.append(
                f"Approved Capital Budget: {context.budget:,.2f} {context.currency}."
            )
        else:
            open_questions.append("Initial capital budget allocation is not specified.")

        # 5. Business Model & Time Horizon
        if context.business_model:
            canonical_facts.append(f"Monetization Model: '{context.business_model}'.")

        if context.time_horizon:
            canonical_facts.append(f"Execution Time Horizon: '{context.time_horizon}'.")
        else:
            assumptions.append(
                "Execution timeline is assumed to be a standard 12-month evaluation horizon."
            )

        # 6. Additional Context
        if context.additional_context:
            canonical_facts.append(f"Qualitative Context Notes: '{context.additional_context}'.")

        # 7. Additional Mode-Specific Open Questions
        if context.mode == BusinessMode.EXISTING_BUSINESS and not context.existing_metrics:
            open_questions.append(
                "Historical operating metrics (e.g. ARR, churn, margins) are not provided for the existing business."
            )

        return SharedBusinessState(
            run_id=run_id,
            business_context=context,
            canonical_facts=canonical_facts,
            constraints=constraints,
            assumptions=assumptions,
            open_questions=open_questions,
            agent_positions=[],
            conflicts=[],
            negotiation_history=[],
            revised_positions=[],
            final_decision=None,
            status=StateStatus.INITIALIZED,
        )

    def validate_state(self, state: SharedBusinessState) -> Tuple[bool, List[str]]:
        """
        Performs deterministic structural and consistency validation on a SharedBusinessState.
        Returns (is_valid, list_of_validation_errors).
        """
        errors = []

        # 1. Run ID Check
        if not state.run_id or not state.run_id.strip():
            errors.append("State is missing a valid run_id.")

        # 2. Business Context & Goal Check
        if not state.business_context:
            errors.append("State is missing underlying BusinessContext.")
        else:
            if not state.business_context.primary_goal or not state.business_context.primary_goal.strip():
                errors.append("BusinessContext primary_goal cannot be empty.")

        # 3. Constraint Consistency Check (Detect duplicate constraints)
        if state.constraints:
            seen = set()
            duplicates = set()
            for c in state.constraints:
                normalized_c = c.strip().lower()
                if normalized_c in seen:
                    duplicates.add(c)
                seen.add(normalized_c)

            if duplicates:
                errors.append(f"Duplicate constraints detected: {list(duplicates)}")

        # 4. Status Check
        if not state.status:
            errors.append("State status is undefined.")

        is_valid = len(errors) == 0
        return is_valid, errors
