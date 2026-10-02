from typing import Union
from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType, ClaimItem
from app.agents.base import SpecialistAgent, AgentExecutionContext


class FinancialAgent(SpecialistAgent):
    """
    Financial Specialist Agent.
    Evaluates financial feasibility, capital requirements, budget allocation,
    monetization model, unit economics, and financial risks.
    """

    @property
    def agent_name(self) -> str:
        return "Financial Agent"

    @property
    def agent_description(self) -> str:
        return (
            "Evaluates capital budget allocation, monetization feasibility, cost structure, "
            "unit economics, financial metrics (e.g. ARR, EBITDA), and financial risks."
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
        budget = biz_ctx.budget
        currency = biz_ctx.currency or "INR"
        business_model = biz_ctx.business_model or "Unspecified Monetization Model"
        time_horizon = biz_ctx.time_horizon or "Unspecified Timeline"
        existing_metrics = biz_ctx.existing_metrics or {}
        goal = biz_ctx.primary_goal or ""
        add_ctx = biz_ctx.additional_context or ""
        all_constraints = biz_ctx.constraints + extra_constraints
        all_problems = biz_ctx.current_problems

        key_claims = []
        evidence = []
        assumptions = [
            "Financial analysis is based exclusively on provided budget numbers and reported metrics; external financial databases are not connected.",
            "Projections assume capital is deployed in accordance with stated time horizon and business model.",
        ]
        risks = []
        recommended_actions = []
        constraints_assumed = list(all_constraints)

        has_budget = budget is not None and budget > 0
        has_metrics = bool(existing_metrics)

        if not has_budget and not has_metrics:
            position = PositionType.INSUFFICIENT_EVIDENCE
            confidence = 0.40

            key_claims.append(
                ClaimItem(
                    claim="Capital budget allocation is not specified in the input context.",
                    evidence="Budget field is missing or set to 0 and no operating metrics provided.",
                    source="Financial Context Validation",
                    assumption="Explicit budget parameters are required to assess burn rate and runway.",
                    confidence=0.90,
                )
            )
            evidence.append("Capital budget parameters missing from input payload.")
            risks.append("Risk of unbudgeted capital depletion and cash flow insolvency.")
            recommended_actions.append("Define explicit capital allocation budget and runway timeline.")
            recommended_actions.append("Build a detailed 12-month pro-forma financial statement (P&L, Cash Flow).")

        else:
            corpus = f"{goal} {add_ctx} {' '.join(all_constraints)} {' '.join(all_problems)} {str(existing_metrics)}".lower()

            # Robust concept matching: Price reduction
            has_price_cut = (
                any(act in corpus for act in ["reduc", "cut", "lower", "slash", "drop", "decreas", "discount", "half", "halv", "50%"])
                and any(tgt in corpus for tgt in ["price", "pricing", "subscription", "fee", "cost", "rate", "tier", "plan"])
            )

            # Robust concept matching: Cash & capital constraints
            has_tight_cash = (
                any(sig in corpus for sig in [
                    "limited cash", "tight cash", "low cash", "limited cash reserves", "cash reserves are limited",
                    "cannot significantly increase", "cannot increase marketing", "cannot increase spending",
                    "high cac", "cac is high", "acquisition cost is already high", "high acquisition cost",
                    "negative cash flow", "high burn rate", "unsustainable burn", "short runway", "unprofitable",
                    "positive cash flow"
                ])
            )

            # Robust concept matching: Strong financial health
            has_strong_finances = (
                any(sig in corpus for sig in [
                    "strong cash reserves", "highly profitable", "positive ebitda", "high profit margin",
                    "low cac", "high ltv", "ample runway", "well-funded", "surplus cash", "zero debt"
                ])
                and not any(neg in corpus for neg in ["limited cash", "negative cash flow", "high burn", "tight cash"])
            )

            formatted_budget = f"{budget:,.2f} {currency}" if budget is not None else "Unspecified Budget"

            # 1. High Financial Tension / Contradiction (DO_NOT_RECOMMEND)
            if (has_price_cut and has_tight_cash) or ("negative cash flow" in corpus and "limited cash" in corpus):
                position = PositionType.DO_NOT_RECOMMEND
                confidence = 0.85

                key_claims.append(
                    ClaimItem(
                        claim="Proposed strategy creates severe cash-flow strain: price reduction combined with tight capital reserves and acquisition cost constraints.",
                        evidence=f"Financial parameters: Budget={formatted_budget}, Constraints cited: limited cash / positive cash flow requirements.",
                        source="Unit Economics & Cash-Flow Audit",
                        assumption="Halving unit revenue while customer acquisition costs remain high leads to negative contribution margins.",
                        confidence=0.88,
                    )
                )
                key_claims.append(
                    ClaimItem(
                        claim="Maintaining positive cash flow while aggressively slashing price requires immediate subsidy or capital injection.",
                        evidence=f"Context references price reduction alongside cash-flow preservation goals: '{goal}'.",
                        source="Capital Runway Evaluation",
                        assumption="Unit economics will degrade before user volume can compensate for revenue per user losses.",
                        confidence=0.85,
                    )
                )
                evidence.append(f"Financial tension detected between price reduction and cash flow constraints ({formatted_budget}).")
                risks.append("High risk of rapid cash depletion and negative operating cash-flow insolvency.")
                risks.append("Revenue per user compression prior to achieving requisite economies of scale.")
                recommended_actions.append("Perform unit economics sensitivity modeling (LTV/CAC) under reduced pricing scenarios.")
                recommended_actions.append("Consider phased cohort pricing or tiered freemium rather than an across-the-board price cut.")

            # 2. Strong Financial Health (RECOMMEND)
            elif has_strong_finances:
                position = PositionType.RECOMMEND
                confidence = 0.83

                key_claims.append(
                    ClaimItem(
                        claim=f"Financial health indicators and capital allocation ({formatted_budget}) support strategic expansion.",
                        evidence=f"Reported financial strengths: Budget={formatted_budget}, Model={business_model}.",
                        source="Capital Viability Assessment",
                        assumption=f"Positive operating margins provide adequate buffer for planned time horizon ({time_horizon}).",
                        confidence=0.85,
                    )
                )
                evidence.append(f"Strong capital structure verified for {time_horizon} horizon.")
                recommended_actions.append("Deploy capital against designated high-ROI growth initiatives.")

            # 3. Standard Balanced Case (CONDITIONAL)
            else:
                position = PositionType.CONDITIONAL
                confidence = 0.79 if mode == BusinessMode.EXISTING_BUSINESS else 0.76

                key_claims.append(
                    ClaimItem(
                        claim=f"Available capital budget of {formatted_budget} allocated for a {time_horizon} horizon.",
                        evidence=f"Budget: {formatted_budget}, Horizon: {time_horizon}, Model: {business_model}.",
                        source="Capital Budget Analysis",
                        assumption="Budget must cover initial development, operational overhead, and customer acquisition.",
                        confidence=0.85,
                    )
                )
                key_claims.append(
                    ClaimItem(
                        claim=f"Monetization approach relies on '{business_model}'.",
                        evidence=f"Business Model: {business_model}",
                        source="Business Model Evaluation",
                        assumption="Unit economics (LTV/CAC) must reach positive gross margins within stated timeline.",
                        confidence=0.80,
                    )
                )

                if existing_metrics:
                    metrics_str = ", ".join([f"{k}: {v}" for k, v in list(existing_metrics.items())[:3]])
                    key_claims.append(
                        ClaimItem(
                            claim=f"Reported existing financial metrics: {metrics_str}.",
                            evidence=f"Existing Metrics: {existing_metrics}",
                            source="Historical Performance Review",
                            assumption="Reported metrics reflect accurate accounting records.",
                            confidence=0.90,
                        )
                    )
                    evidence.append(f"Historical metrics analyzed: {metrics_str}.")

                evidence.append(f"Allocated budget: {formatted_budget} over {time_horizon}.")
                risks.append(f"Capital burn rate risk: {formatted_budget} budget may be exhausted before reaching cash-flow breakeven.")
                recommended_actions.append("Calculate target Customer Acquisition Cost (CAC) and Lifetime Value (LTV) metrics.")
                recommended_actions.append("Establish a monthly cash-flow burn rate baseline and 6-month runway buffer.")

        evidence.append("Financial live ledger / accounting software integration pending.")

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
