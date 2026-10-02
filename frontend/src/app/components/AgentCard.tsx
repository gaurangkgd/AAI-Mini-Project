"use client";

import React from "react";
import type { AgentPosition, PositionType } from "@/app/types";

export interface AgentCardProps {
  position: AgentPosition;
}

export function AgentCard({ position }: AgentCardProps) {
  const {
    agent_name,
    position: posType,
    confidence,
    key_claims,
    evidence,
  } = position;

  const formattedConfidence = `${(confidence * 100).toFixed(0)}%`;

  const getStyleForPosition = (pos: PositionType | string) => {
    switch (pos.toLowerCase()) {
      case "recommend":
        return {
          title: "RECOMMEND",
          badge: "bg-emerald-950/80 text-emerald-400 border-emerald-800/80",
          cardBorder: "border-zinc-800 hover:border-emerald-800/60",
        };
      case "conditional":
        return {
          title: "CONDITIONAL",
          badge: "bg-amber-950/80 text-amber-400 border-amber-800/80",
          cardBorder: "border-zinc-800 hover:border-amber-800/60",
        };
      case "do_not_recommend":
        return {
          title: "DO NOT RECOMMEND",
          badge: "bg-rose-950/80 text-rose-400 border-rose-800/80",
          cardBorder: "border-zinc-800 hover:border-rose-800/60",
        };
      case "insufficient_evidence":
      default:
        return {
          title: "INSUFFICIENT EVIDENCE",
          badge: "bg-zinc-900 text-zinc-400 border-zinc-700",
          cardBorder: "border-zinc-800",
        };
    }
  };

  const style = getStyleForPosition(posType);

  return (
    <div
      className={`w-full p-5 bg-zinc-900/60 border ${style.cardBorder} rounded-xl shadow-lg space-y-4 text-zinc-100 transition-all`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div>
          <h4 className="font-bold text-base text-zinc-100">{agent_name}</h4>
          <span className="text-xs text-zinc-400 font-mono">
            Confidence: <span className="text-zinc-200">{formattedConfidence}</span>
          </span>
        </div>
        <span
          className={`px-2.5 py-1 rounded-full border text-xs font-extrabold tracking-wide uppercase ${style.badge}`}
        >
          {style.title}
        </span>
      </div>

      {/* Rationale & Key Claims */}
      {key_claims && key_claims.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-zinc-800/80">
          <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider block">
            Key Reasoning
          </span>
          <ul className="space-y-1.5 text-xs text-zinc-300">
            {key_claims.slice(0, 3).map((item, idx) => (
              <li key={idx} className="flex items-start gap-1.5 leading-relaxed">
                <span className="text-indigo-400 font-bold">•</span>
                <span>{item.claim}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Evidence Status */}
      <div className="pt-2 border-t border-zinc-800/80 flex items-center justify-between text-xs text-zinc-400">
        <span>Evidence Items Cited</span>
        <span className="font-mono font-semibold text-zinc-200">
          {evidence ? evidence.length : 0}
        </span>
      </div>
    </div>
  );
}
