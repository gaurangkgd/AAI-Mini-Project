from typing import Union
from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType, ClaimItem
from app.agents.base import SpecialistAgent, AgentExecutionContext


class CustomerAgent(SpecialistAgent):
    """
    Customer Specialist Agent.
    Evaluates customer segment needs, user pain points, value proposition alignment,
    adoption friction, customer retention, and churn factors.
    """

    @property
    def agent_name(self) -> str:
        return "Customer Agent"

    @property
    def agent_description(self) -> str:
        return (
            "Evaluates customer demographics, pain points, value proposition fit, "
            "user friction points, adoption willingness, and retention/churn metrics."
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
        problems = biz_ctx.current_problems
        metrics = biz_ctx.existing_metrics or {}
        goal = biz_ctx.primary_goal or ""
        add_ctx = biz_ctx.additional_context or ""
        all_constraints = biz_ctx.constraints + extra_constraints

        key_claims = []
        evidence = []
        assumptions = [
            "Customer sentiment analysis relies strictly on provided target market definitions and reported pain points; external survey APIs are not active.",
            "Customer willingness to pay correlates with severity of identified pain points and price accessibility.",
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
                    claim="Target market demographic is unspecified, preventing user pain-point analysis.",
                    evidence="Target market field is empty in input context.",
                    source="Customer Persona Validation",
                    assumption="Evaluating customer adoption willingness requires explicit buyer persona definition.",
                    confidence=0.90,
                )
            )
            evidence.append("Target market demographic missing from input parameters.")
            risks.append("Risk of building product features that fail to address real customer pain points.")
            recommended_actions.append(
                "Map out detailed target customer personas, buying process, and key decision makers."
            )

        else:
            corpus = f"{target_market} {goal} {add_ctx} {' '.join(problems)} {' '.join(all_constraints)} {str(metrics)}".lower()

            # Normalized customer friction signals
            severe_friction_signals = [
                "severe churn", "declining nps", "customers unwilling to pay", "strong backlash",
                "poor retention", "high dissatisfaction", "customer boycott", "massive churn",
                "customers rejecting", "widespread customer complaints"
            ]
            has_severe_friction = any(sig in corpus for sig in severe_friction_signals)

            # Normalized strong customer adoption / value-fit signals
            strong_adoption_signals = [
                "loved by users", "high nps", "strong user love", "high referral", "high retention",
                "urgent customer pain", "raving fans", "urgent pain point"
            ]

            # Robust price reduction concept
            has_price_reduction = (
                any(act in corpus for act in ["reduc", "cut", "lower", "slash", "drop", "decreas", "discount", "half", "halv", "50%"])
                and any(tgt in corpus for tgt in ["price", "pricing", "subscription", "fee", "cost", "rate", "tier", "plan"])
            )

            # Robust price-sensitive demographic
            is_student_or_budget_segment = any(
                term in corpus for term in ["student", "students", "college", "youth", "price-sensitive", "price sensitive", "budget-conscious"]
            )
            has_strong_student_fit = is_student_or_budget_segment and has_price_reduction

            has_strong_adoption = any(sig in corpus for sig in strong_adoption_signals) or has_strong_student_fit

            # 1. Customer Rejection / Friction (DO_NOT_RECOMMEND)
            if has_severe_friction:
                position = PositionType.DO_NOT_RECOMMEND
                confidence = 0.82

                key_claims.append(
                    ClaimItem(
                        claim=f"High customer attrition and adoption resistance detected in target segment '{target_market}'.",
                        evidence=f"Reported customer friction signals: {', '.join([s for s in severe_friction_signals if s in corpus])}.",
                        source="Customer Churn & Sentiment Review",
                        assumption="Failing to resolve root customer dissatisfaction accelerates user churn.",
                        confidence=0.85,
                    )
                )
                evidence.append(f"Customer dissatisfaction indicators detected in {target_market}.")
                risks.append("Risk of accelerated customer churn and negative brand word-of-mouth.")
                recommended_actions.append("Halt aggressive growth initiatives and conduct immediate churn root-cause interviews.")

            # 2. High Customer Adoption Fit (RECOMMEND)
            elif has_strong_adoption:
                position = PositionType.RECOMMEND
                confidence = 0.84

                if has_strong_student_fit:
                    key_claims.append(
                        ClaimItem(
                            claim=f"Proposed pricing adjustments strongly align with the purchasing power of target demographic '{target_market}'.",
                            evidence=f"Target segment '{target_market}' is price-sensitive; price reduction significantly lowers barrier to adoption.",
                            source="Customer Affordability & Adoption Fit Analysis",
                            assumption="Affordable price point unlocks latent customer demand and accelerates organic student onboarding.",
                            confidence=0.88,
                        )
                    )
                    evidence.append(f"Strong adoption affinity verified for price-sensitive demographic '{target_market}'.")
                else:
                    key_claims.append(
                        ClaimItem(
                            claim=f"Target customer segment '{target_market}' exhibits strong product-value resonance and high adoption signals.",
                            evidence="Customer satisfaction indicators identified in context.",
                            source="Customer Advocacy Evaluation",
                            assumption="Strong customer sentiment provides organic growth momentum.",
                            confidence=0.85,
                        )
                    )
                    evidence.append(f"High customer sentiment verified in {target_market}.")

                recommended_actions.append(f"Deploy referral incentives to capitalize on high adoption willingness in {target_market}.")

            # 3. Standard Balanced Case (CONDITIONAL)
            else:
                position = PositionType.CONDITIONAL
                confidence = 0.78 if mode == BusinessMode.EXISTING_BUSINESS else 0.76

                key_claims.append(
                    ClaimItem(
                        claim=f"Target customer base in '{target_market}' requires ongoing value proposition validation.",
                        evidence=f"Target Market: '{target_market}'; Strategic Goal: '{goal}'.",
                        source="Customer Persona Analysis",
                        assumption="Customer willingness to adopt requires ongoing feature alignment.",
                        confidence=0.85,
                    )
                )

                if problems:
                    prob_str = ", ".join(problems[:2])
                    key_claims.append(
                        ClaimItem(
                            claim=f"Identified customer pain points to solve: {prob_str}.",
                            evidence=f"Current Problems list: {problems}",
                            source="Customer Pain-Point Review",
                            assumption="Solving reported pain points drives customer retention.",
                            confidence=0.85,
                        )
                    )
                    evidence.append(f"Analyzed reported pain points: {prob_str}.")

                evidence.append(f"Evaluated customer segment impact for venture in '{target_market}'.")
                risks.append("Risk of customer inertia or dissatisfaction if product updates disrupt workflow.")
                recommended_actions.append("Run problem validation interviews with at least 15 target buyers.")
                recommended_actions.append("Establish a Net Promoter Score (NPS) baseline before strategic rollout.")

        evidence.append("External survey / CRM tool integration pending.")

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
