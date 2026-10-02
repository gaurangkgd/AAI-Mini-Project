"use client";

import React from "react";
import type { Conflict } from "@/app/types";

export interface ConflictSectionProps {
  conflicts: Conflict[];
}

export function ConflictSection({ conflicts }: ConflictSectionProps) {
  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return "bg-rose-950/80 text-rose-400 border-rose-800/80";
      case "high":
        return "bg-amber-950/80 text-amber-400 border-amber-800/80";
      case "medium":
        return "bg-indigo-950/80 text-indigo-400 border-indigo-800/80";
      case "low":
      default:
        return "bg-zinc-900 text-zinc-400 border-zinc-700";
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "resolved":
        return "bg-emerald-950/80 text-emerald-400 border-emerald-800/80";
      case "unresolved":
      case "open":
        return "bg-amber-950/80 text-amber-400 border-amber-800/80";
      case "escalated":
        return "bg-rose-950/80 text-rose-400 border-rose-800/80";
      default:
        return "bg-zinc-900 text-zinc-400 border-zinc-700";
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto my-8 space-y-4 text-zinc-100">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold tracking-tight text-zinc-100">
          Detected Conflicts
        </h3>
        <span className="text-xs text-zinc-400 font-mono">
          {conflicts.length} Disagreements
        </span>
      </div>

      {conflicts.length === 0 ? (
        <div className="p-6 bg-zinc-900/40 border border-zinc-800 rounded-xl text-center text-zinc-400 text-sm">
          No significant conflicts detected across agents.
        </div>
      ) : (
        <div className="space-y-4">
          {conflicts.map((item) => (
            <div
              key={item.conflict_id}
              className="p-5 bg-zinc-900/60 border border-zinc-800 rounded-xl space-y-4 shadow-lg"
            >
              {/* Card Header */}
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-800/80 pb-3">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-indigo-400 uppercase font-semibold">
                    {item.conflict_type.replace(/_/g, " ")}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded border text-[10px] font-bold uppercase ${getSeverityBadge(
                      item.severity
                    )}`}
                  >
                    {item.severity} severity
                  </span>
                </div>

                <span
                  className={`px-2 py-0.5 rounded border text-[10px] font-bold uppercase ${getStatusBadge(
                    item.status
                  )}`}
                >
                  {item.status}
                </span>
              </div>

              {/* Agents Involved */}
              <div className="text-xs text-zinc-400">
                <span className="font-medium text-zinc-300">Agents Involved: </span>
                <span className="font-mono text-zinc-200">
                  {item.agents_involved.join(" vs ")}
                </span>
              </div>

              {/* Description */}
              <p className="text-sm text-zinc-200 leading-relaxed">
                {item.description}
              </p>

              {/* Conflicting Claims */}
              {item.conflicting_claims && item.conflicting_claims.length > 0 && (
                <div className="space-y-1.5 pt-2">
                  <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider block">
                    Conflicting Claims
                  </span>
                  <ul className="space-y-1 text-xs text-zinc-300">
                    {item.conflicting_claims.map((claim, idx) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-rose-400 font-bold">•</span>
                        <span>{claim}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Resolution Summary */}
              {item.resolution && (
                <div className="p-3 bg-emerald-950/30 border border-emerald-800/50 rounded-lg text-xs space-y-1">
                  <span className="font-semibold text-emerald-400 uppercase tracking-wider block">
                    Resolution Outcome
                  </span>
                  <p className="text-zinc-200">{item.resolution}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
