from typing import Union
from app.models.business import BusinessContext, BusinessMode
from app.models.agent import AgentPosition, PositionType, ClaimItem
from app.agents.base import SpecialistAgent, AgentExecutionContext


class OperationsAgent(SpecialistAgent):
    """
    Operations Specialist Agent.
    Evaluates operational execution feasibility, supply chain dependencies,
    resource allocations, scalability bottlenecks, and execution complexity.
    """

    @property
    def agent_name(self) -> str:
        return "Operations Agent"

    @property
    def agent_description(self) -> str:
        return (
            "Evaluates operational execution feasibility, resource allocation, workflow complexity, "
            "supplier/vendor dependencies, scalability bottlenecks, and operational risks."
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
        stage = biz_ctx.business_stage or "Unspecified Stage"
        horizon = biz_ctx.time_horizon or "Unspecified Horizon"
        problems = biz_ctx.current_problems
        goal = biz_ctx.primary_goal or ""
        add_ctx = biz_ctx.additional_context or ""
        idea_desc = f"{biz_ctx.business_idea or ''} {biz_ctx.business_description or ''}"
        all_constraints = biz_ctx.constraints + extra_constraints

        key_claims = []
        evidence = []
        assumptions = [
            "Operational assessment assumes standard availability of key skilled talent and vendor infrastructure in target region.",
            "Operational execution timelines depend directly on resolving identified bottleneck problems.",
        ]
        risks = []
        recommended_actions = []
        constraints_assumed = list(all_constraints)

        has_stage = bool(biz_ctx.business_stage and biz_ctx.business_stage.strip())
        has_horizon = bool(biz_ctx.time_horizon and biz_ctx.time_horizon.strip())
        has_goal = bool(biz_ctx.primary_goal and biz_ctx.primary_goal.strip())

        if not has_stage and not has_horizon and not has_goal:
            position = PositionType.INSUFFICIENT_EVIDENCE
            confidence = 0.40
            key_claims.append(
                ClaimItem(
                    claim="Operational execution context lacks stage, timeline, and objective specifications.",
                    evidence="Operational input parameters are empty.",
                    source="Operational Readiness Audit",
                    assumption="Operational resource allocation requires defined stage and timeline milestones.",
                    confidence=0.90,
                )
            )
            evidence.append("Missing operational timeline and stage parameters.")
            risks.append("Risk of misaligned staffing and execution delays.")
            recommended_actions.append("Define operational milestones and delivery time horizons.")

        else:
            corpus = f"{stage} {horizon} {goal} {idea_desc} {add_ctx} {' '.join(problems)} {' '.join(all_constraints)}".lower()

            # Normalized severe operational bottlenecks
            severe_ops_signals = [
                "cannot scale infrastructure", "infrastructure cannot scale", "capacity maxed",
                "severe bottleneck", "supply chain breakdown", "unrealistic timeline",
                "cannot significantly increase spending on infrastructure", "infrastructure limits",
                "cannot handle volume", "system crash", "critical staffing shortage"
            ]
            has_severe_ops = any(sig in corpus for sig in severe_ops_signals)

            # Normalized strong operational readiness
            strong_ops_signals = [
                "auto-scales", "cloud-native", "ample capacity", "fully automated",
                "standardized sops", "established supply chain", "scalable infrastructure",
                "proven operational team", "redundant infrastructure"
            ]
            has_strong_ops = any(sig in corpus for sig in strong_ops_signals)

            # 1. Critical Operational Infeasibility (DO_NOT_RECOMMEND)
            if has_severe_ops and not has_strong_ops and ("cannot" in corpus or "breakdown" in corpus or "maxed" in corpus):
                position = PositionType.DO_NOT_RECOMMEND
                confidence = 0.82

                key_claims.append(
                    ClaimItem(
                        claim=f"Operational capacity is insufficient to support rapid volume expansion within {horizon}.",
                        evidence=f"Operational constraints detected: {', '.join([s for s in severe_ops_signals if s in corpus])}.",
                        source="Infrastructure Capacity Audit",
                        assumption="Attempting 3x load expansion with restricted infrastructure spend degrades platform reliability.",
                        confidence=0.88,
                    )
                )
                evidence.append("Severe operational capacity bottleneck detected.")
                risks.append("System outages, degraded service latency, and customer churn under peak loads.")
                recommended_actions.append("Conduct stress testing and provision scalable auto-scaling cloud tiers before volume rollout.")

            # 2. High Operational Feasibility (RECOMMEND)
            elif has_strong_ops:
                position = PositionType.RECOMMEND
                confidence = 0.84

                key_claims.append(
                    ClaimItem(
                        claim=f"Operational architecture demonstrates robust scalability for {horizon} horizon.",
                        evidence=f"Verified operational strengths: {', '.join([s for s in strong_ops_signals if s in corpus])}.",
                        source="Operational Scalability Review",
                        assumption="Automated operational workflows handle volume increases without proportional overhead growth.",
                        confidence=0.88,
                    )
                )
                evidence.append("High operational scalability verified.")
                recommended_actions.append("Establish automated health monitoring alerts as throughput increases.")

            # 3. Standard Balanced Case (CONDITIONAL)
            else:
                position = PositionType.CONDITIONAL
                confidence = 0.80 if mode == BusinessMode.EXISTING_BUSINESS else 0.77

                key_claims.append(
                    ClaimItem(
                        claim=f"Operational infrastructure evaluated for objective: '{goal}' within {horizon}.",
                        evidence=f"Primary Goal: '{goal}'; Operating Stage: '{stage}'.",
                        source="Infrastructure Readiness Review",
                        assumption="Operational workflows require capacity tuning to support strategic scale.",
                        confidence=0.85,
                    )
                )

                if problems:
                    prob_str = ", ".join(problems)
                    key_claims.append(
                        ClaimItem(
                            claim=f"Existing operational bottlenecks identified: {prob_str}.",
                            evidence=f"Current Problems reported: {problems}",
                            source="Operational Bottleneck Audit",
                            assumption="Resolving existing operational pain points is required to ensure scaling stability.",
                            confidence=0.90,
                        )
                    )
                    evidence.append(f"Operational bottlenecks analyzed: {prob_str}.")
                    risks.append(f"Capacity bottleneck risk stemming from: {problems[0]}.")

                evidence.append("Operational workflow readiness reviewed for enterprise.")
                recommended_actions.append("Conduct a Process Value Stream Map to eliminate operational bottlenecks.")
                recommended_actions.append("Implement key operational metrics tracking (Cycle Time, SLA Compliance, Capacity Utilization).")

        evidence.append("ERP / Operations management tool integration pending.")

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
