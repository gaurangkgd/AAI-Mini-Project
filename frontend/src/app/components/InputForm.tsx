"use client";

import React, { useState } from "react";
import type { BusinessContext, BusinessMode } from "@/app/types";

export interface InputFormProps {
  onSubmit: (context: BusinessContext) => void;
}

interface MetricPair {
  key: string;
  value: string;
}

export function InputForm({ onSubmit }: InputFormProps) {
  const [mode, setMode] = useState<BusinessMode>("new_startup");

  // Common Fields
  const [businessName, setBusinessName] = useState("");
  const [primaryGoal, setPrimaryGoal] = useState("");
  const [industry, setIndustry] = useState("");
  const [targetMarket, setTargetMarket] = useState("");
  const [geography, setGeography] = useState("");
  const [businessModel, setBusinessModel] = useState("");
  const [businessStage, setBusinessStage] = useState("");
  const [budget, setBudget] = useState<string>("");
  const [currency, setCurrency] = useState("INR");
  const [timeHorizon, setTimeHorizon] = useState("");
  const [additionalContext, setAdditionalContext] = useState("");

  // Mode Specific Fields
  const [businessIdea, setBusinessIdea] = useState("");
  const [businessDescription, setBusinessDescription] = useState("");

  // Array / Dict fields (raw UI text state)
  const [constraintsText, setConstraintsText] = useState("");
  const [currentProblemsText, setCurrentProblemsText] = useState("");
  const [metricsList, setMetricsList] = useState<MetricPair[]>([
    { key: "", value: "" },
  ]);

  // Errors
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleAddMetric = () => {
    setMetricsList([...metricsList, { key: "", value: "" }]);
  };

  const handleRemoveMetric = (index: number) => {
    setMetricsList(metricsList.filter((_, i) => i !== index));
  };

  const handleMetricChange = (
    index: number,
    field: "key" | "value",
    val: string
  ) => {
    const updated = [...metricsList];
    updated[index][field] = val;
    setMetricsList(updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: Record<string, string> = {};

    if (!primaryGoal.trim()) {
      newErrors.primaryGoal = "Primary strategic goal is required.";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});

    // Parse constraints & problems into string[]
    const constraints = constraintsText
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    const current_problems = currentProblemsText
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    // Parse metrics into Record<string, unknown>
    const existing_metrics: Record<string, unknown> = {};
    for (const pair of metricsList) {
      if (pair.key.trim()) {
        const rawVal = pair.value.trim();
        // Try parsing number if numeric
        if (rawVal !== "" && !isNaN(Number(rawVal))) {
          existing_metrics[pair.key.trim()] = Number(rawVal);
        } else {
          existing_metrics[pair.key.trim()] = rawVal;
        }
      }
    }

    const numericBudget =
      budget.trim() !== "" && !isNaN(Number(budget)) ? Number(budget) : null;

    const payload: BusinessContext = {
      mode,
      business_name: businessName.trim() || null,
      business_idea: businessIdea.trim() || null,
      business_description: businessDescription.trim() || null,
      industry: industry.trim() || null,
      target_market: targetMarket.trim() || null,
      geography: geography.trim() || null,
      business_model: businessModel.trim() || null,
      business_stage: businessStage.trim() || null,
      primary_goal: primaryGoal.trim(),
      budget: numericBudget,
      currency: currency.trim() || "INR",
      time_horizon: timeHorizon.trim() || null,
      constraints,
      current_problems,
      existing_metrics,
      additional_context: additionalContext.trim() || null,
    };

    onSubmit(payload);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-4xl mx-auto space-y-8 bg-zinc-900/60 border border-zinc-800 p-6 sm:p-8 rounded-2xl shadow-xl text-zinc-100"
    >
      {/* SECTION 1 — MODE SELECTION */}
      <div className="space-y-3">
        <label className="block text-sm font-semibold text-zinc-300 uppercase tracking-wider">
          Section 1 — Mode Selection
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <button
            type="button"
            onClick={() => setMode("new_startup")}
            className={`flex flex-col p-4 rounded-xl border text-left transition-all ${
              mode === "new_startup"
                ? "bg-indigo-950/50 border-indigo-500 shadow-md shadow-indigo-500/10"
                : "bg-zinc-950/40 border-zinc-800 hover:border-zinc-700"
            }`}
          >
            <div className="flex items-center justify-between w-full mb-1">
              <span className="font-bold text-lg text-zinc-100">
                Startup Idea Evaluation
              </span>
              <span
                className={`h-3 w-3 rounded-full ${
                  mode === "new_startup" ? "bg-indigo-500" : "bg-zinc-700"
                }`}
              />
            </div>
            <p className="text-xs text-zinc-400">
              Evaluate a new venture idea, target market fit, business model,
              and execution feasibility.
            </p>
          </button>

          <button
            type="button"
            onClick={() => setMode("existing_business")}
            className={`flex flex-col p-4 rounded-xl border text-left transition-all ${
              mode === "existing_business"
                ? "bg-indigo-950/50 border-indigo-500 shadow-md shadow-indigo-500/10"
                : "bg-zinc-950/40 border-zinc-800 hover:border-zinc-700"
            }`}
          >
            <div className="flex items-center justify-between w-full mb-1">
              <span className="font-bold text-lg text-zinc-100">
                Existing Business Strategy
              </span>
              <span
                className={`h-3 w-3 rounded-full ${
                  mode === "existing_business" ? "bg-indigo-500" : "bg-zinc-700"
                }`}
              />
            </div>
            <p className="text-xs text-zinc-400">
              Analyze strategic decisions, optimization challenges, and bottleneck
              resolution for established businesses.
            </p>
          </button>
        </div>
      </div>

      {/* SECTION 2 — CORE BUSINESS CONTEXT */}
      <div className="space-y-4 pt-4 border-t border-zinc-800">
        <label className="block text-sm font-semibold text-zinc-300 uppercase tracking-wider">
          Section 2 — Core Business Context
        </label>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1">
              Business Name
            </label>
            <input
              type="text"
              placeholder="e.g. EcoClean Tech"
              value={businessName}
              onChange={(e) => setBusinessName(e.target.value)}
              className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1">
              Industry / Sector
            </label>
            <input
              type="text"
              placeholder="e.g. CleanTech, SaaS, Logistics"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-zinc-400 mb-1">
            Primary Strategic Goal <span className="text-rose-500">*</span>
          </label>
          <input
            type="text"
            placeholder="e.g. Evaluate market entry feasibility for European operations"
            value={primaryGoal}
            onChange={(e) => setPrimaryGoal(e.target.value)}
            className={`w-full bg-zinc-950/80 border rounded-lg px-3 py-2 text-sm focus:outline-none ${
              errors.primaryGoal
                ? "border-rose-500 focus:border-rose-500"
                : "border-zinc-800 focus:border-indigo-500"
            }`}
          />
          {errors.primaryGoal && (
            <p className="text-xs text-rose-500 mt-1">{errors.primaryGoal}</p>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1">
              Business Stage
            </label>
            <input
              type="text"
              placeholder="e.g. Idea, MVP, Seed, Growth, Enterprise"
              value={businessStage}
              onChange={(e) => setBusinessStage(e.target.value)}
              className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1">
              Business Model
            </label>
            <input
              type="text"
              placeholder="e.g. B2B SaaS, Marketplace, Subscription"
              value={businessModel}
              onChange={(e) => setBusinessModel(e.target.value)}
              className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* SECTION 3 — MODE-SPECIFIC DETAILS */}
      <div className="space-y-4 pt-4 border-t border-zinc-800">
        <label className="block text-sm font-semibold text-zinc-300 uppercase tracking-wider">
          Section 3 — {mode === "new_startup" ? "Startup Details" : "Operational Context"}
        </label>

        {mode === "new_startup" ? (
          <>
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1">
                Business Idea / Concept
              </label>
              <input
                type="text"
                placeholder="e.g. Autonomous AI-driven recycling sorting system"
                value={businessIdea}
                onChange={(e) => setBusinessIdea(e.target.value)}
                className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1">
                Business Description
              </label>
              <textarea
                rows={3}
                placeholder="Describe your planned operations, target value proposition, or product line..."
                value={businessDescription}
                onChange={(e) => setBusinessDescription(e.target.value)}
                className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-zinc-400 mb-1">
                  Target Market Segment
                </label>
                <input
                  type="text"
                  placeholder="e.g. Mid-sized municipal waste management companies"
                  value={targetMarket}
                  onChange={(e) => setTargetMarket(e.target.value)}
                  className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-400 mb-1">
                  Target Geography
                </label>
                <input
                  type="text"
                  placeholder="e.g. North America, Western Europe"
                  value={geography}
                  onChange={(e) => setGeography(e.target.value)}
                  className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          </>
        ) : (
          <>
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1">
                Current Problems / Bottlenecks (one per line)
              </label>
              <textarea
                rows={3}
                placeholder="e.g. High customer acquisition cost (CAC)\nHigh churn rate in Q3\nOperational capacity limits"
                value={currentProblemsText}
                onChange={(e) => setCurrentProblemsText(e.target.value)}
                className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 font-mono text-xs"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1">
                Existing Business Metrics
              </label>
              <div className="space-y-2">
                {metricsList.map((item, idx) => (
                  <div key={idx} className="flex gap-2 items-center">
                    <input
                      type="text"
                      placeholder="Metric Name (e.g. ARR)"
                      value={item.key}
                      onChange={(e) =>
                        handleMetricChange(idx, "key", e.target.value)
                      }
                      className="flex-1 bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-indigo-500"
                    />
                    <input
                      type="text"
                      placeholder="Value (e.g. 500000)"
                      value={item.value}
                      onChange={(e) =>
                        handleMetricChange(idx, "value", e.target.value)
                      }
                      className="flex-1 bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-indigo-500"
                    />
                    {metricsList.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveMetric(idx)}
                        className="px-2.5 py-1.5 bg-rose-950/40 text-rose-400 border border-rose-800/60 rounded-lg text-xs hover:bg-rose-900/60"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                ))}
                <button
                  type="button"
                  onClick={handleAddMetric}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium pt-1"
                >
                  + Add Metric
                </button>
              </div>
            </div>
          </>
        )}

        <div>
          <label className="block text-xs font-medium text-zinc-400 mb-1">
            Constraints & Limitations (one per line)
          </label>
          <textarea
            rows={2}
            placeholder="e.g. Regulatory GDPR compliance\nMax timeline 6 months\nStrict budget limit"
            value={constraintsText}
            onChange={(e) => setConstraintsText(e.target.value)}
            className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 font-mono text-xs"
          />
        </div>
      </div>

      {/* SECTION 4 — FINANCIALS & TIMELINE */}
      <div className="space-y-4 pt-4 border-t border-zinc-800">
        <label className="block text-sm font-semibold text-zinc-300 uppercase tracking-wider">
          Section 4 — Financials & Timeline
        </label>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1">
              Budget
            </label>
            <input
              type="number"
              min="0"
              placeholder="e.g. 500000"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1">
              Currency
            </label>
            <input
              type="text"
              placeholder="INR, USD, EUR"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1">
              Time Horizon
            </label>
            <input
              type="text"
              placeholder="e.g. 6 months, 2 years"
              value={timeHorizon}
              onChange={(e) => setTimeHorizon(e.target.value)}
              className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-zinc-400 mb-1">
            Additional Context / Notes
          </label>
          <textarea
            rows={2}
            placeholder="Any other details, competitor context, or qualitative background..."
            value={additionalContext}
            onChange={(e) => setAdditionalContext(e.target.value)}
            className="w-full bg-zinc-950/80 border border-zinc-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      <div className="pt-4 border-t border-zinc-800 flex justify-end">
        <button
          type="submit"
          className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/20 transition-all text-sm"
        >
          Submit Business Context
        </button>
      </div>
    </form>
  );
}
