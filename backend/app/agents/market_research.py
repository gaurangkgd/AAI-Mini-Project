from typing import Union
from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType, ClaimItem
from app.agents.base import SpecialistAgent, AgentExecutionContext


class MarketResearchAgent(SpecialistAgent):
    """
    Market Research Specialist Agent.
    Evaluates market demand, target audience alignment, geographic dynamics,
    and market feasibility across both new startup ideas and existing businesses.
    """

    @property
    def agent_name(self) -> str:
        return "Market Research Agent"

    @property
    def agent_description(self) -> str:
        return (
            "Evaluates market demand, target customer demographics, industry trends, "
            "geographic expansion feasibility, and market-related risks."
        )

    def analyze(
        self, context: Union[BusinessContext, AgentExecutionContext]
    ) -> AgentPosition:
        if isinstance(context, AgentExecutionContext):
            biz_ctx = context.business_context
            extra_constraints = context.constraints
        else:
            biz_ctx = context
            extra_constraints = []

        mode = biz_ctx.mode
        industry = biz_ctx.industry or "Unspecified Industry"
        target_market = biz_ctx.target_market
        geography = biz_ctx.geography or "Unspecified Region"
        goal = biz_ctx.primary_goal or ""
        idea_or_desc = (
            biz_ctx.business_idea
            or biz_ctx.business_description
            or biz_ctx.business_name
            or "Proposed Venture"
        )
        add_ctx = biz_ctx.additional_context or ""

        all_constraints = biz_ctx.constraints + extra_constraints
        all_problems = biz_ctx.current_problems

        key_claims = []
        evidence = []
        assumptions = [
            "Analysis is derived strictly from provided business parameters; real-time external search APIs are not active in this phase.",
            "Market adoption assumes standard industry adoption curves for the targeted sector.",
        ]
        risks = []
        recommended_actions = []
        constraints_assumed = list(all_constraints)

        # Evaluate market data presence
        has_target_market = bool(target_market and target_market.strip())
        has_industry = bool(biz_ctx.industry and biz_ctx.industry.strip())

        if not has_target_market or not has_industry:
            position = PositionType.INSUFFICIENT_EVIDENCE
            confidence = 0.35

            if not has_target_market:
                key_claims.append(
                    ClaimItem(
                        claim="Target market demographic is insufficiently defined.",
                        evidence="Target market field is missing or empty in business context.",
                        source="BusinessContext Input Validation",
                        assumption="Specific market segment parameters are required to evaluate market size and CAC.",
                        confidence=0.90,
                    )
                )
                recommended_actions.append(
                    "Define explicit customer personas, target demographics, and market segment boundaries."
                )

            if not has_industry:
                key_claims.append(
                    ClaimItem(
                        claim="Industry sector classification is missing.",
                        evidence="Industry field is empty in business context.",
                        source="BusinessContext Input Validation",
                        assumption="Industry categorization is necessary to evaluate TAM/SAM and regulatory trends.",
                        confidence=0.90,
                    )
                )
                recommended_actions.append(
                    "Specify the primary industry sector (e.g., SaaS, HealthTech, CleanTech)."
                )

            risks.append(
                "High risk of misdirected go-to-market strategy due to undefined target audience."
            )
            evidence.append("User input lacks detailed target market or industry specifications.")

        else:
            # Check market signals across full context
            corpus = f"{goal} {idea_or_desc} {add_ctx} {' '.join(all_problems)} {' '.join(all_constraints)}".lower()

            # 1. Check for strong negative market signals (DO_NOT_RECOMMEND)
            negative_market_signals = [
                "shrinking market", "dying industry", "saturated market", "no demand",
                "declining market", "zero demand", "market rejecting", "banned market",
                "obsolete technology", "unviable market"
            ]
            has_negative_market = any(sig in corpus for sig in negative_market_signals)

            # 2. Check for strong positive market tailwinds (RECOMMEND)
            positive_market_signals = [
                "rapidly growing", "high demand", "validated demand", "strong tailwinds",
                "underserved market", "massive market demand", "fast growing", "proven demand",
                "strong market interest", "market boom"
            ]
            has_positive_market = any(sig in corpus for sig in positive_market_signals)

            if has_negative_market:
                position = PositionType.DO_NOT_RECOMMEND
                confidence = 0.82
                key_claims.append(
                    ClaimItem(
                        claim=f"Target market indicators in {industry} suggest severe market contraction or adverse demand conditions.",
                        evidence=f"Reported market signals: {', '.join([s for s in negative_market_signals if s in corpus])}.",
                        source="Market Trend Analysis",
                        assumption="Entering a contracting or saturated market presents unviable customer acquisition economics.",
                        confidence=0.88,
                    )
                )
                risks.append(f"Severe market demand contraction risk for {idea_or_desc} in {industry}.")
                recommended_actions.append("Pivot core value proposition toward an adjacent growing market sector.")

            elif has_positive_market:
                position = PositionType.RECOMMEND
                confidence = 0.84
                key_claims.append(
                    ClaimItem(
                        claim=f"Strong market demand tailwinds identified for '{target_market}' in {industry}.",
                        evidence=f"Identified growth signals in market context for {geography}.",
                        source="Market Opportunity Evaluation",
                        assumption="Target demographic exhibits strong willingness to adopt within specified geography.",
                        confidence=0.85,
                    )
                )
                evidence.append(f"Favorable market expansion indicators in {geography}.")
                recommended_actions.append(f"Accelerate go-to-market rollout to capture market share in {target_market}.")

            else:
                # Balanced standard condition
                position = PositionType.CONDITIONAL
                confidence = 0.78 if mode == BusinessMode.EXISTING_BUSINESS else 0.75

                key_claims.append(
                    ClaimItem(
                        claim=f"Proposed initiative targets defined market segment '{target_market}' in {industry}.",
                        evidence=f"Target Market: '{target_market}'; Region: '{geography}'.",
                        source="BusinessContext Input Analysis",
                        assumption="Target customer demand exists within the specified geographic region.",
                        confidence=0.80,
                    )
                )
                key_claims.append(
                    ClaimItem(
                        claim=f"Primary strategic goal ('{goal}') requires empirical customer validation in {geography}.",
                        evidence=f"Strategic Objective: '{goal}'",
                        source="Strategic Alignment Analysis",
                        assumption="Early customer interviews can validate product-market fit prior to full capital deployment.",
                        confidence=0.85,
                    )
                )

                evidence.append(f"Target segment '{target_market}' identified within {industry} in {geography}.")
                risks.append(f"Market acceptance risk for '{idea_or_desc}' in {geography} without empirical pilot validation.")
                recommended_actions.append(f"Conduct 20+ qualitative interviews with representatives of '{target_market}'.")
                recommended_actions.append("Perform quantitative TAM/SAM addressable market sizing for the targeted region.")

        evidence.append("Live web search integration pending; findings based on input context validation.")

        return AgentPosition(
            agent_name=self.agent_name,
            position=position,
            confidence=confidence,
            key_claims=key_claims,
            evidence=evidence,
            assumptions=assumptions,
            constraints_assumed=constraints_assumed,
            risks=risks,
            recommended_actions=recommended_actions,
        )
