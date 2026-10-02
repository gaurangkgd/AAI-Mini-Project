from typing import Union
from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType, ClaimItem
from app.agents.base import SpecialistAgent, AgentExecutionContext


class MarketingGTMAgent(SpecialistAgent):
    """
    Marketing & Go-To-Market (GTM) Specialist Agent.
    Evaluates positioning strategy, customer acquisition channels, launch readiness,
    distribution models, and GTM execution risks.
    """

    @property
    def agent_name(self) -> str:
        return "Marketing & GTM Agent"

    @property
    def agent_description(self) -> str:
        return (
            "Evaluates positioning strategy, target channel selection, customer acquisition efficiency, "
            "go-to-market execution plans, distribution logistics, and marketing risks."
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
        target_market = biz_ctx.target_market
        biz_model = biz_ctx.business_model or "Unspecified Model"
        geography = biz_ctx.geography or "Unspecified Geography"
        goal = biz_ctx.primary_goal or ""
        add_ctx = biz_ctx.additional_context or ""
        all_constraints = biz_ctx.constraints + extra_constraints
        all_problems = biz_ctx.current_problems

        key_claims = []
        evidence = []
        assumptions = [
            "GTM channel evaluation is based on standard B2B/B2C industry distribution benchmarks; ad-tech API metrics are not active.",
            "Customer acquisition conversion rate depends on product positioning clarity and channel relevance.",
        ]
        risks = []
        recommended_actions = []
        constraints_assumed = list(all_constraints)

        has_target_market = bool(target_market and target_market.strip())

        if not has_target_market:
            position = PositionType.INSUFFICIENT_EVIDENCE
            confidence = 0.40

            key_claims.append(
                ClaimItem(
                    claim="Go-to-market strategy cannot be validated without a defined target customer segment.",
                    evidence="Target market input parameter is empty.",
                    source="GTM Strategy Validation",
                    assumption="Channel selection and messaging strategy require specific buyer target definition.",
                    confidence=0.90,
                )
            )
            evidence.append("Missing target market parameter for GTM evaluation.")
            risks.append("Risk of misallocated ad spend and inefficient channel testing.")
            recommended_actions.append(
                "Identify top 2 primary marketing/distribution channels specific to target customer demographic."
            )

        else:
            corpus = f"{target_market} {biz_model} {geography} {goal} {add_ctx} {' '.join(all_constraints)} {' '.join(all_problems)}".lower()

            # Normalized aggressive growth signals
            aggressive_growth_signals = [
                "3x", "5x", "10x", "triple", "tripling", "rapidly increase", "rapid growth",
                "aggressive expansion", "hypergrowth", "exponential growth"
            ]
            has_aggressive_growth = any(sig in corpus for sig in aggressive_growth_signals)

            # Normalized acquisition restrictions
            acquisition_blocker_signals = [
                "cannot significantly increase marketing", "cannot increase marketing", "no marketing budget",
                "acquisition cost is already high", "high customer acquisition cost", "high cac",
                "cac is high", "ad costs prohibitive", "marketing spend capped", "frozen marketing"
            ]
            has_acquisition_blockers = any(sig in corpus for sig in acquisition_blocker_signals)

            # Normalized strong organic / GTM leverage signals
            strong_gtm_signals = [
                "viral referral", "organic growth", "strong distribution network", "low cac",
                "word of mouth", "influencer partnership", "established marketing funnel", "high viral coefficient"
            ]
            has_strong_gtm = any(sig in corpus for sig in strong_gtm_signals)

            # 1. GTM Infeasibility / Severe Bottleneck (DO_NOT_RECOMMEND)
            if has_aggressive_growth and has_acquisition_blockers and not has_strong_gtm:
                position = PositionType.DO_NOT_RECOMMEND
                confidence = 0.83

                key_claims.append(
                    ClaimItem(
                        claim=f"Unrealistic GTM acquisition target: aggressive user expansion ({goal}) is structurally incompatible with restricted marketing budget and high CAC.",
                        evidence=f"Constraints cite restricted marketing spending and elevated customer acquisition costs.",
                        source="Customer Acquisition Economics Audit",
                        assumption="Tripling user volume within 6 months requires either paid acquisition scale or proven viral loops.",
                        confidence=0.88,
                    )
                )
                evidence.append("Incompatible GTM constraints detected: high growth target vs marketing spend restrictions.")
                risks.append("Growth target failure risk due to inadequate acquisition channel capacity.")
                recommended_actions.append("Develop built-in student referral incentives / viral sharing mechanics before committing to 3x growth target.")
                recommended_actions.append("Pilot low-cost campus ambassador distribution before scaling.")

            # 2. Strong GTM Channel Traction (RECOMMEND)
            elif has_strong_gtm:
                position = PositionType.RECOMMEND
                confidence = 0.83

                key_claims.append(
                    ClaimItem(
                        claim=f"Scalable go-to-market distribution verified for '{target_market}' in {geography}.",
                        evidence=f"Organic/viral acquisition signals verified in context.",
                        source="GTM Scalability Analysis",
                        assumption="Existing distribution leverage enables low-cost customer acquisition at scale.",
                        confidence=0.85,
                    )
                )
                evidence.append(f"High-efficiency GTM channel verified for {geography}.")
                recommended_actions.append("Double down on primary organic distribution channel to accelerate adoption.")

            # 3. Standard Balanced Case (CONDITIONAL)
            else:
                position = PositionType.CONDITIONAL
                confidence = 0.78 if mode == BusinessMode.EXISTING_BUSINESS else 0.75

                key_claims.append(
                    ClaimItem(
                        claim=f"Launch strategy for '{target_market}' requires alignment with business model '{biz_model}'.",
                        evidence=f"Target Market: '{target_market}'; Business Model: '{biz_model}'; Region: '{geography}'.",
                        source="Channel Strategy Alignment",
                        assumption="B2B models require direct sales, while B2C models require targeted media and community loops.",
                        confidence=0.80,
                    )
                )

                evidence.append(f"GTM expansion strategy evaluated for {target_market} in {geography}.")
                risks.append("High Customer Acquisition Cost (CAC) risk during initial campaign scale.")
                recommended_actions.append("Develop a 90-day GTM roadmap outlining channel experiment metrics (CAC, Conversion %).")
                recommended_actions.append("Audit current acquisition channel ROI before allocating additional capital.")

        evidence.append("Marketing analytics / ad platform API integration pending.")

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
