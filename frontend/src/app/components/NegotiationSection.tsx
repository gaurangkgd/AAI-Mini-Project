"use client";

import React from "react";
import type { AgentPosition, NegotiationRound, PositionType } from "@/app/types";

export interface NegotiationSectionProps {
  history: NegotiationRound[];
  originalPositions: AgentPosition[];
  revisedPositions: AgentPosition[];
}

export function NegotiationSection({
  history,
  originalPositions,
  revisedPositions,
}: NegotiationSectionProps) {
  const getBadgeStyle = (pos: PositionType | string) => {
    switch (pos.toLowerCase()) {
      case "recommend":
        return "bg-emerald-950/80 text-emerald-400 border-emerald-800/80";
      case "conditional":
        return "bg-amber-950/80 text-amber-400 border-amber-800/80";
      case "do_not_recommend":
        return "bg-rose-950/80 text-rose-400 border-rose-800/80";
      case "insufficient_evidence":
      default:
        return "bg-zinc-900 text-zinc-400 border-zinc-700";
    }
  };

  // Map agent names to their original and revised positions for comparison
  const agentMap = new Map<
    string,
    { original?: AgentPosition; revised?: AgentPosition }
  >();

  originalPositions.forEach((pos) => {
    agentMap.set(pos.agent_name, {
      ...agentMap.get(pos.agent_name),
      original: pos,
    });
  });

  revisedPositions.forEach((pos) => {
    agentMap.set(pos.agent_name, {
      ...agentMap.get(pos.agent_name),
      revised: pos,
    });
  });

  const positionComparisons = Array.from(agentMap.entries()).map(
    ([agentName, data]) => {
      const origPos = data.original?.position ?? "N/A";
      const revPos = data.revised?.position ?? origPos;
      const changed = data.revised && origPos !== revPos;
      return {
        agentName,
        origPos,
        revPos,
        changed,
      };
    }
  );

  return (
    <div className="w-full max-w-6xl mx-auto my-8 space-y-6 text-zinc-100">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold tracking-tight text-zinc-100">
          Agent Negotiation
        </h3>
        <span className="text-xs text-zinc-400 font-mono">
          {history.length} Round{history.length === 1 ? "" : "s"} Conducted
        </span>
      </div>

      {history.length === 0 ? (
        <div className="p-6 bg-zinc-900/40 border border-zinc-800 rounded-xl text-center text-zinc-400 text-sm">
          No negotiation was required — specialist agents reached natural
          consensus.
        </div>
      ) : (
        <div className="space-y-6">
          {/* Position Shift Summary Banner */}
          <div className="p-5 bg-zinc-900/60 border border-zinc-800 rounded-xl space-y-3 shadow-lg">
            <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider block">
              Position Shifts Post-Negotiation
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {positionComparisons.map((item) => (
                <div
                  key={item.agentName}
                  className={`p-3 rounded-lg border text-xs space-y-1.5 ${
                    item.changed
                      ? "bg-indigo-950/40 border-indigo-700/60"
                      : "bg-zinc-950/60 border-zinc-800"
                  }`}
                >
                  <div className="font-semibold text-zinc-200">
                    {item.agentName}
                  </div>
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span
                      className={`px-1.5 py-0.5 rounded border text-[10px] uppercase font-bold ${getBadgeStyle(
                        item.origPos
                      )}`}
                    >
                      {item.origPos}
                    </span>
                    {item.changed ? (
                      <>
                        <span className="text-indigo-400 font-bold">→</span>
                        <span
                          className={`px-1.5 py-0.5 rounded border text-[10px] uppercase font-bold ${getBadgeStyle(
                            item.revPos
                          )}`}
                        >
                          {item.revPos}
                        </span>
                      </>
                    ) : (
                      <span className="text-[10px] text-zinc-500 italic ml-1">
                        (Unchanged)
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Negotiation History Rounds */}
          <div className="space-y-4">
            {history.map((round) => (
              <div
                key={round.round_number}
                className="p-5 bg-zinc-900/60 border border-zinc-800 rounded-xl space-y-4 shadow-lg"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-800/80 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-400 border border-indigo-800/80 text-xs font-bold uppercase font-mono">
                      Round {round.round_number}
                    </span>
                    <span className="text-xs text-zinc-300 font-medium">
                      Issue: {round.issue}
                    </span>
                  </div>
                  {round.resolution && (
                    <span className="px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 text-[10px] font-bold uppercase">
                      Resolved
                    </span>
                  )}
                </div>

                <div className="text-xs text-zinc-400">
                  <span className="font-medium text-zinc-300">
                    Participants:{" "}
                  </span>
                  <span className="font-mono text-zinc-200">
                    {round.participants.join(", ")}
                  </span>
                </div>

                {round.arguments && round.arguments.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider block">
                      Arguments Exchanged
                    </span>
                    <ul className="space-y-1 text-xs text-zinc-300">
                      {round.arguments.map((arg, idx) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="text-indigo-400 font-bold">•</span>
                          <span>{arg}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {round.resolution && (
                  <div className="p-3 bg-emerald-950/30 border border-emerald-800/50 rounded-lg text-xs space-y-1">
                    <span className="font-semibold text-emerald-400 uppercase tracking-wider block">
                      Round Resolution
                    </span>
                    <p className="text-zinc-200">{round.resolution}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
