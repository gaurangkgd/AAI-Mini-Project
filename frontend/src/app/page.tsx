"use client";

import React, { useState } from "react";
import { AgentGrid } from "@/app/components/AgentGrid";
import { ConflictSection } from "@/app/components/ConflictSection";
import { FinalDecisionPanel } from "@/app/components/FinalDecisionPanel";
import { InputForm } from "@/app/components/InputForm";
import { LoadingState } from "@/app/components/LoadingState";
import { NegotiationSection } from "@/app/components/NegotiationSection";
import { RiskSection } from "@/app/components/RiskSection";
import { orchestrate } from "@/app/lib/api";
import type { BusinessContext, SharedBusinessState } from "@/app/types";

type PageStatus = "input" | "loading" | "completed" | "error";

export default function Home() {
  const [status, setStatus] = useState<PageStatus>("input");
  const [result, setResult] = useState<SharedBusinessState | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (context: BusinessContext) => {
    setStatus("loading");
    setErrorMessage(null);

    try {
      const data = await orchestrate(context);
      setResult(data);
      setStatus("completed");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "An unexpected error occurred.";
      setErrorMessage(message);
      setStatus("error");
    }
  };

  const handleReset = () => {
    setStatus("input");
    setResult(null);
    setErrorMessage(null);
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-4 sm:p-8 bg-zinc-950 text-zinc-100 selection:bg-indigo-500 selection:text-white">
      <div className="max-w-4xl w-full text-center space-y-4 mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 text-xs font-semibold tracking-wider text-indigo-400 uppercase bg-indigo-950/70 border border-indigo-800/60 rounded-full">
          Problem Statement 27 (PS-27)
        </div>

        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-zinc-100 via-zinc-300 to-zinc-500 bg-clip-text text-transparent">
          Multi-Agent Business &amp; Startup Strategy Advisor
        </h1>

        <p className="text-sm sm:text-base text-zinc-400 font-normal leading-relaxed max-w-2xl mx-auto">
          Collaborative Multi-Agent Coordination System for autonomous startup
          evaluation and strategic business decision intelligence.
        </p>
      </div>

      <div className="w-full">
        {status === "input" && <InputForm onSubmit={handleSubmit} />}

        {status === "loading" && <LoadingState />}

        {status === "completed" && result && (
          <div className="space-y-8 w-full">
            <FinalDecisionPanel state={result} onReset={handleReset} />
            <AgentGrid positions={result.agent_positions} />
            <ConflictSection conflicts={result.conflicts} />
            <NegotiationSection
              history={result.negotiation_history}
              originalPositions={result.agent_positions}
              revisedPositions={result.revised_positions}
            />
            <RiskSection
              finalDecision={result.final_decision}
              agentPositions={result.agent_positions}
            />
          </div>
        )}

        {status === "error" && (
          <div className="max-w-2xl mx-auto w-full my-8 p-6 bg-zinc-900/80 border border-rose-900/60 rounded-2xl shadow-xl space-y-6 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 text-xs font-semibold tracking-wider text-rose-400 uppercase bg-rose-950/60 border border-rose-800/60 rounded-full">
              Analysis Failed
            </div>

            <p className="text-sm text-zinc-300 leading-relaxed max-w-lg mx-auto bg-zinc-950 p-4 rounded-xl border border-zinc-800 text-left font-mono text-xs text-rose-300">
              {errorMessage}
            </p>

            <button
              onClick={handleReset}
              className="px-6 py-2.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-semibold rounded-xl border border-zinc-700 transition-all text-sm"
            >
              Try Again
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
