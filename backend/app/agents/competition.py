from typing import Union
from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType, ClaimItem
from app.agents.base import SpecialistAgent, AgentExecutionContext


class CompetitionAgent(SpecialistAgent):
    """
    Competition Specialist Agent.
    Evaluates competitive dynamics, differentiation factors, potential substitutes,
    entry barriers, and competitive risk parameters.
    """

    @property
    def agent_name(self) -> str:
        return "Competition Agent"

    @property
    def agent_description(self) -> str:
        return (
            "Evaluates competitive environment, market substitutes, direct/indirect competitors, "
            "differentiation advantages, barriers to entry, and competitive risks."
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
        add_context = biz_ctx.additional_context or ""
        goal = biz_ctx.primary_goal or ""
        idea_desc = f"{biz_ctx.business_idea or ''} {biz_ctx.business_description or ''}"
        all_constraints = biz_ctx.constraints + extra_constraints

        key_claims = []
        evidence = []
        assumptions = [
            "Competitive analysis relies on provided business context parameters; external competitor research databases are not connected in this phase.",
            "Incumbent market players are assumed to possess established distribution advantages in mature industry sectors.",
        ]
        risks = []
        recommended_actions = []
        constraints_assumed = list(all_constraints)

        has_industry = bool(biz_ctx.industry and biz_ctx.industry.strip())

        if not has_industry:
            position = PositionType.INSUFFICIENT_EVIDENCE
            confidence = 0.40

            key_claims.append(
                ClaimItem(
                    claim="Industry sector is unspecified, preventing competitive intensity baseline evaluation.",
                    evidence="Industry field is empty in input context.",
                    source="Competitive Context Validation",
                    assumption="Competitive benchmarking requires an established industry sector classification.",
                    confidence=0.90,
                )
            )
            evidence.append("Missing industry sector classification in input.")
            risks.append("Risk of unmitigated entry by established incumbents or low-cost substitutes.")
            recommended_actions.append(
                "Specify primary industry and identify key direct and indirect competitor categories."
            )

        else:
            corpus = f"{industry} {goal} {idea_desc} {add_context} {' '.join(all_constraints)}".lower()

            # Normalized competitive signals
            severe_competition_signals = [
                "monopoly", "dominant incumbent", "price war", "commoditized", "no differentiation",
                "easily copied", "easily replicated", "entrenched competitors", "overwhelming competition",
                "competitor owns 90%", "fierce price war", "brutal price competition"
            ]
            has_severe_comp = any(sig in corpus for sig in severe_competition_signals)

            strong_moat_signals = [
                "proprietary technology", "patented", "exclusive partnership", "high switching cost",
                "high switching costs", "strong moat", "unique ip", "first mover advantage",
                "defensible moat", "distinct competitive advantage", "proprietary algorithm"
            ]
            has_strong_moat = any(sig in corpus for sig in strong_moat_signals)

            # 1. Severe Competitive Disadvantage (DO_NOT_RECOMMEND)
            if has_severe_comp and not has_strong_moat:
                position = PositionType.DO_NOT_RECOMMEND
                confidence = 0.81

                key_claims.append(
                    ClaimItem(
                        claim=f"High competitive risk in '{industry}': commoditized product dynamics and intense incumbent pressure threaten viability.",
                        evidence=f"Competitive signals identified in context: {', '.join([s for s in severe_competition_signals if s in corpus])}.",
                        source="Competitive Structure Audit",
                        assumption="Compromising pricing or margins without defensible moats exposes business to predatory pricing from incumbents.",
                        confidence=0.85,
                    )
                )
                evidence.append(f"High competitive saturation detected in {industry}.")
                risks.append("Margin collapse driven by aggressive competitor price-matching or established incumbent distribution.")
                recommended_actions.append("Develop proprietary operational or technological differentiation before competing on price.")

            # 2. Defensible Competitive Position (RECOMMEND)
            elif has_strong_moat:
                position = PositionType.RECOMMEND
                confidence = 0.83

                key_claims.append(
                    ClaimItem(
                        claim=f"Defensible competitive moat identified for venture in '{industry}'.",
                        evidence=f"Proprietary advantage indicators identified: {', '.join([s for s in strong_moat_signals if s in corpus])}.",
                        source="Moat Evaluation",
                        assumption="Proprietary differentiation creates barriers to entry protecting operating margins.",
                        confidence=0.88,
                    )
                )
                evidence.append(f"Strong defensibility verified in {industry}.")
                recommended_actions.append("Leverage technological/operational moat to capture high-margin market share.")

            # 3. Standard Balanced Case (CONDITIONAL)
            else:
                position = PositionType.CONDITIONAL
                confidence = 0.77 if mode == BusinessMode.EXISTING_BUSINESS else 0.74

                key_claims.append(
                    ClaimItem(
                        claim=f"Positioning in '{industry}' requires continuous differentiation against market alternatives.",
                        evidence=f"Industry: '{industry}'; Target Market: '{target_market or 'Unspecified'}'.",
                        source="Market Structure Analysis",
                        assumption="Incumbents will react if market share shifts noticeably in target segment.",
                        confidence=0.80,
                    )
                )

                if "competitor" in add_context.lower() or "competition" in add_context.lower():
                    key_claims.append(
                        ClaimItem(
                            claim="User provided explicit notes regarding competitive context.",
                            evidence=f"Additional Context snippet: {add_context[:120]}...",
                            source="Qualitative Context Review",
                            assumption="Provided competitive notes accurately reflect ground realities.",
                            confidence=0.85,
                        )
                    )
                    evidence.append("Incorporated user-supplied competitive notes.")

                evidence.append(f"Competitive landscape evaluated within '{industry}' sector.")
                risks.append(f"Risk of margin compression if competitors replicate core value proposition in {industry}.")
                recommended_actions.append("Conduct a formal Feature Matrix & Differentiation Benchmark against top 3 market alternatives.")
                recommended_actions.append("Identify technical or operational moats (IP, proprietary workflow, network effects).")

        evidence.append("External web search / competitor API integration pending.")

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
