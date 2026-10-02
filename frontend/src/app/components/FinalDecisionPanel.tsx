"use client";

import React from "react";
import type { PositionType, SharedBusinessState } from "@/app/types";

export interface FinalDecisionPanelProps {
  state: SharedBusinessState;
  onReset: () => void;
}

export function FinalDecisionPanel({
  state,
  onReset,
}: FinalDecisionPanelProps) {
  const decision = state.final_decision;
  const rawRec = decision?.recommendation ?? "insufficient_evidence";
  const confidence = decision?.confidence ?? 0;

  const formattedConfidence = `${(confidence * 100).toFixed(1)}%`;

  const getStyleForRecommendation = (rec: PositionType | string) => {
    switch (rec.toLowerCase()) {
      case "recommend":
        return {
          title: "RECOMMEND",
          badge: "bg-emerald-950/80 text-emerald-400 border-emerald-800/80",
          cardBorder: "border-emerald-800/60",
          glow: "shadow-emerald-500/10",
        };
      case "conditional":
        return {
          title: "CONDITIONAL RECOMMENDATION",
          badge: "bg-amber-950/80 text-amber-400 border-amber-800/80",
          cardBorder: "border-amber-800/60",
          glow: "shadow-amber-500/10",
        };
      case "do_not_recommend":
        return {
          title: "DO NOT RECOMMEND",
          badge: "bg-rose-950/80 text-rose-400 border-rose-800/80",
          cardBorder: "border-rose-800/60",
          glow: "shadow-rose-500/10",
        };
      case "insufficient_evidence":
      default:
        return {
          title: "INSUFFICIENT EVIDENCE",
          badge: "bg-zinc-900 text-zinc-400 border-zinc-700",
          cardBorder: "border-zinc-800",
          glow: "shadow-zinc-500/5",
        };
    }
  };

  const style = getStyleForRecommendation(rawRec);

  return (
    <div
      className={`w-full max-w-2xl mx-auto my-8 p-8 bg-zinc-900/80 border ${style.cardBorder} rounded-2xl shadow-xl ${style.glow} space-y-6 text-center text-zinc-100`}
    >
      <div className="space-y-2">
        <span className="text-xs font-semibold tracking-wider text-zinc-400 uppercase">
          Final Decision Synthesis
        </span>
        <div>
          <div
            className={`inline-block px-4 py-2 rounded-full border text-sm font-extrabold tracking-wide uppercase ${style.badge}`}
          >
            {style.title}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 py-4 border-y border-zinc-800/80">
        <div className="bg-zinc-950/60 p-4 rounded-xl border border-zinc-800/60 space-y-1">
          <span className="text-xs text-zinc-400 font-medium">
            Analytical Confidence
          </span>
          <div className="text-2xl font-bold text-zinc-100">
            {formattedConfidence}
          </div>
        </div>

        <div className="bg-zinc-950/60 p-4 rounded-xl border border-zinc-800/60 space-y-1">
          <span className="text-xs text-zinc-400 font-medium">Run ID</span>
          <div className="text-xs font-mono text-indigo-400 truncate pt-1">
            {state.run_id || "N/A"}
          </div>
        </div>
      </div>

      <div className="pt-2 flex justify-center">
        <button
          onClick={onReset}
          className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/20 transition-all text-sm"
        >
          Start New Analysis
        </button>
      </div>
    </div>
  );
}
