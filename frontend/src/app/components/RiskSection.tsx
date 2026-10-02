"use client";

import React from "react";
import type { AgentPosition, FinalDecision } from "@/app/types";

export interface RiskSectionProps {
  finalDecision: FinalDecision | null;
  agentPositions: AgentPosition[];
}

export function RiskSection({ finalDecision, agentPositions }: RiskSectionProps) {
  const synthesizedRisks: string[] = finalDecision?.risks ?? [];

  // Collect per-agent domain risks — only agents that have at least one risk entry
  const agentRisks: { agentName: string; risks: string[] }[] = agentPositions
    .filter((pos) => pos.risks && pos.risks.length > 0)
    .map((pos) => ({ agentName: pos.agent_name, risks: pos.risks }));

  const hasAnything = synthesizedRisks.length > 0 || agentRisks.length > 0;
  const totalCount = synthesizedRisks.length + agentRisks.reduce((acc, a) => acc + a.risks.length, 0);

  return (
    <div className="w-full max-w-6xl mx-auto my-8 space-y-6 text-zinc-100">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold tracking-tight text-zinc-100">
          Key Risks
        </h3>
        <span className="text-xs text-zinc-400 font-mono">
          {totalCount} Risk{totalCount === 1 ? "" : "s"} Identified
        </span>
      </div>

      {!hasAnything ? (
        /* ── Empty State ─────────────────────────────────────────── */
        <div className="p-6 bg-zinc-900/40 border border-zinc-800 rounded-xl text-center text-zinc-400 text-sm">
          No risks were identified by the analysis.
        </div>
      ) : (
        <div className="space-y-6">
          {/* ── Synthesized Risks ────────────────────────────────── */}
          {synthesizedRisks.length > 0 && (
            <div className="p-5 bg-zinc-900/60 border border-zinc-800 rounded-xl space-y-3 shadow-lg">
              <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider block">
                Synthesized Risks
              </span>
              <p className="text-[11px] text-zinc-500 leading-relaxed">
                Aggregated and prioritised risks from the final decision synthesis.
              </p>
              <ul className="space-y-2">
                {synthesizedRisks.map((risk, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-3 p-3 bg-amber-950/20 border border-amber-800/40 rounded-lg"
                  >
                    {/* Risk index pill */}
                    <span className="mt-0.5 flex-shrink-0 w-5 h-5 flex items-center justify-center rounded-full bg-amber-950/80 border border-amber-700/60 text-amber-400 text-[10px] font-bold font-mono">
                      {idx + 1}
                    </span>
                    <span className="text-xs text-zinc-200 leading-relaxed">{risk}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* ── Per-Agent Domain Risks ────────────────────────────── */}
          {agentRisks.length > 0 && (
            <div className="space-y-3">
              <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider block px-1">
                Domain-Specific Risks by Agent
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {agentRisks.map(({ agentName, risks }) => (
                  <div
                    key={agentName}
                    className="p-4 bg-zinc-900/60 border border-zinc-800 rounded-xl space-y-3 shadow-md"
                  >
                    {/* Agent label */}
                    <div className="flex items-center gap-2 pb-2 border-b border-zinc-800/80">
                      <span className="w-2 h-2 rounded-full bg-rose-500 flex-shrink-0" />
                      <span className="text-xs font-semibold text-zinc-200 tracking-tight">
                        {agentName}
                      </span>
                      <span className="ml-auto text-[10px] text-zinc-500 font-mono">
                        {risks.length} risk{risks.length === 1 ? "" : "s"}
                      </span>
                    </div>

                    {/* Risk list */}
                    <ul className="space-y-2">
                      {risks.map((risk, idx) => (
                        <li
                          key={idx}
                          className="flex items-start gap-2 text-xs text-zinc-300 leading-relaxed"
                        >
                          <span className="mt-1.5 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-rose-500/70" />
                          {risk}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
