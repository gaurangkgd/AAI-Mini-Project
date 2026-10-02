"use client";

import React from "react";
import { AgentCard } from "@/app/components/AgentCard";
import type { AgentPosition } from "@/app/types";

export interface AgentGridProps {
  positions: AgentPosition[];
}

export function AgentGrid({ positions }: AgentGridProps) {
  if (!positions || positions.length === 0) {
    return null;
  }

  return (
    <div className="w-full max-w-6xl mx-auto my-8 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-zinc-100 tracking-tight">
          Specialist Perspectives
        </h3>
        <span className="text-xs text-zinc-400 font-mono">
          {positions.length} Agents Evaluated
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {positions.map((pos) => (
          <AgentCard key={pos.agent_name} position={pos} />
        ))}
      </div>
    </div>
  );
}
