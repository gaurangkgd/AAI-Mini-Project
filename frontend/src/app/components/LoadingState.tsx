"use client";

import React from "react";

export function LoadingState() {
  return (
    <div className="w-full max-w-2xl mx-auto my-12 p-8 bg-zinc-900/60 border border-zinc-800 rounded-2xl text-center space-y-6 shadow-xl">
      <div className="flex justify-center">
        <div className="relative flex items-center justify-center">
          <div className="h-16 w-16 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin" />
          <div className="absolute h-8 w-8 rounded-full bg-indigo-500/20 animate-pulse" />
        </div>
      </div>

      <div className="space-y-2">
        <h2 className="text-xl font-bold text-zinc-100 tracking-tight">
          Analyzing your business decision...
        </h2>
        <p className="text-sm text-zinc-400 max-w-md mx-auto leading-relaxed">
          Seven specialist agents are analyzing your business decision. The
          system will check for conflicts and synthesize their findings.
        </p>
      </div>

      <div className="inline-flex items-center gap-2 px-3 py-1.5 text-xs text-indigo-400 bg-indigo-950/50 border border-indigo-800/60 rounded-full font-mono">
        <span className="h-2 w-2 rounded-full bg-indigo-400 animate-ping" />
        Multi-Agent Orchestrator Running
      </div>
    </div>
  );
}
