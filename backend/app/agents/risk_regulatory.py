from typing import Union
from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType, ClaimItem
from app.agents.base import SpecialistAgent, AgentExecutionContext


class RiskRegulatoryAgent(SpecialistAgent):
    """
    Risk & Regulatory Specialist Agent.
    Evaluates regulatory compliance questions, legal dependencies, data privacy/tech risks,
    operational liability risks, and assumptions requiring verification.
    DISCLAIMER: Provides strategic risk analysis, not formal legal advice.
    """

    @property
    def agent_name(self) -> str:
        return "Risk & Regulatory Agent"

    @property
    def agent_description(self) -> str:
        return (
            "Evaluates regulatory compliance questions, legal exposure, data privacy/security dependencies, "
            "licensing requirements, liability risks, and systemic business uncertainties."
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
        
        # Infer geography from target_market or description if not explicitly set
        geography = biz_ctx.geography
        if not geography:
            tm = (biz_ctx.target_market or "").lower()
            if "india" in tm:
                geography = "India"
            elif "europe" in tm:
                geography = "Europe"
            elif "us" in tm or "usa" in tm or "america" in tm:
                geography = "United States"
            else:
                geography = "Unspecified Geography"

        goal = biz_ctx.primary_goal or ""
        add_ctx = biz_ctx.additional_context or ""
        desc = biz_ctx.business_description or ""
        all_constraints = biz_ctx.constraints + extra_constraints

        key_claims = []
        evidence = []
        assumptions = [
            "THIS ANALYSIS DOES NOT CONSTITUTE FORMAL LEGAL ADVICE. Formal compliance requires licensed legal counsel review.",
            "Regulatory frameworks vary significantly by jurisdiction; compliance must be verified against local laws.",
        ]
        risks = []
        recommended_actions = []
        constraints_assumed = list(all_constraints)

        has_industry = bool(biz_ctx.industry and biz_ctx.industry.strip())
        has_geo = geography != "Unspecified Geography"

        if not has_industry and not has_geo and not desc and not goal:
            position = PositionType.INSUFFICIENT_EVIDENCE
            confidence = 0.40
            key_claims.append(
                ClaimItem(
                    claim="Industry and jurisdiction parameters are unspecified, preventing statutory compliance review.",
                    evidence="Industry and geography fields are empty.",
                    source="Regulatory Environment Screening",
                    assumption="Statutory risk analysis requires industry classification and regional jurisdiction.",
                    confidence=0.90,
                )
            )
            evidence.append("Missing jurisdiction and industry sector classification.")
            risks.append("Unknown statutory exposure and licensing compliance risk.")
            recommended_actions.append("Specify primary operating jurisdiction and industry classification.")

        else:
            corpus = f"{industry} {geography} {goal} {desc} {add_ctx} {' '.join(all_constraints)}".lower()

            # Normalized severe regulatory blockers
            severe_reg_signals = [
                "regulatory ban", "illegal", "unlicensed in jurisdiction", "dgca ban",
                "gdpr non-compliant", "regulatory shutdown", "court injunction", "statutory violation",
                "banned by law", "criminal liability"
            ]
            has_severe_reg = any(sig in corpus for sig in severe_reg_signals)

            # Normalized low-risk / certified compliance signals
            strong_compliance_signals = [
                "fully licensed", "fully compliant", "no special regulatory licensing",
                "standard digital service", "low regulatory risk", "certified compliance",
                "iso certified", "soc2 certified"
            ]
            has_strong_compliance = any(sig in corpus for sig in strong_compliance_signals)

            # 1. Critical Regulatory Blocker (DO_NOT_RECOMMEND)
            if has_severe_reg:
                position = PositionType.DO_NOT_RECOMMEND
                confidence = 0.86

                key_claims.append(
                    ClaimItem(
                        claim=f"Severe regulatory non-compliance blocker detected in '{industry}' ({geography}).",
                        evidence=f"Regulatory blockers reported: {', '.join([s for s in severe_reg_signals if s in corpus])}.",
                        source="Statutory Risk Audit",
                        assumption="Operating under explicit regulatory prohibition creates immediate existential legal liability.",
                        confidence=0.95,
                    )
                )
                evidence.append("Critical statutory regulatory risk detected.")
                risks.append("Regulatory sanctions, statutory fines, or operational injunction.")
                recommended_actions.append("Engage specialized regulatory legal counsel to resolve statutory prohibitions.")

            # 2. Verified Low Regulatory Risk (RECOMMEND)
            elif has_strong_compliance and not any("regulat" in c.lower() for c in all_constraints):
                position = PositionType.RECOMMEND
                confidence = 0.83

                key_claims.append(
                    ClaimItem(
                        claim=f"Regulatory posture in '{industry}' ({geography}) is clear with low statutory friction.",
                        evidence=f"Compliance indicators verified: {', '.join([s for s in strong_compliance_signals if s in corpus])}.",
                        source="Jurisdictional Risk Assessment",
                        assumption="Standard commercial operations within this segment do not require specialized government licenses.",
                        confidence=0.88,
                    )
                )
                evidence.append(f"Clear regulatory path confirmed in {geography}.")
                recommended_actions.append("Maintain routine data security and customer privacy compliance audits.")

            # 3. Standard Balanced Case (CONDITIONAL)
            else:
                position = PositionType.CONDITIONAL
                confidence = 0.79 if mode == BusinessMode.EXISTING_BUSINESS else 0.76

                key_claims.append(
                    ClaimItem(
                        claim=f"Business operation in '{industry}' within '{geography}' is subject to statutory regulatory frameworks.",
                        evidence=f"Industry: '{industry}'; Region: '{geography}'.",
                        source="Regulatory Environment Screening",
                        assumption="Regulated commercial operations require appropriate consumer terms and data privacy safeguards.",
                        confidence=0.85,
                    )
                )

                reg_constraints = [
                    c for c in all_constraints
                    if any(term in c.lower() for term in ["regulat", "legal", "complian", "dgca", "iso", "hipaa", "permit", "license"])
                ]
                if reg_constraints:
                    key_claims.append(
                        ClaimItem(
                            claim=f"Identified explicit regulatory/compliance constraints: {', '.join(reg_constraints)}.",
                            evidence=f"Regulatory constraints: {reg_constraints}",
                            source="Input Constraint Review",
                            assumption="Failure to satisfy specified regulatory constraints exposes business to legal liability.",
                            confidence=0.90,
                        )
                    )
                    evidence.append(f"Identified explicit compliance constraints: {', '.join(reg_constraints)}.")
                    risks.append(f"Regulatory non-compliance risk related to: {reg_constraints[0]}.")

                evidence.append(f"Regulatory screening executed for {geography}.")
                risks.append("Regulatory delay or liability risk during scale.")
                recommended_actions.append(f"Engage a qualified legal specialist in {geography} to audit statutory licensing for {industry}.")
                recommended_actions.append("Draft comprehensive Terms of Service, Privacy Policy, and Data Security compliance protocols.")

        evidence.append("Legal database / regulatory API integration pending.")

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
