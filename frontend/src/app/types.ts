/**
 * types.ts
 *
 * TypeScript type definitions mirroring the backend Pydantic models exactly.
 * Generated from inspection of:
 *   - backend/app/models/business.py
 *   - backend/app/models/agent.py
 *   - backend/app/models/state.py
 *
 * Conventions:
 *   - Python Optional[T]            → TypeScript T | null
 *   - Python List[T]  (default=[]) → TypeScript T[]
 *   - Python Dict[str, Any]         → TypeScript Record<string, unknown>
 *   - Python str Enum               → TypeScript string union
 *   - Python float [0,1]            → TypeScript number
 *   - Python int                    → TypeScript number
 *
 * This file contains ONLY types — no runtime code.
 */

// ---------------------------------------------------------------------------
// BusinessContext
// ---------------------------------------------------------------------------

/** Supported operation modes for business analysis. */
export type BusinessMode = "new_startup" | "existing_business";

/**
 * Canonical business context model representing input parameters
 * for both Startup Idea Evaluation and Existing Business Strategic Decision Support.
 * Mirrors: backend/app/models/business.py :: BusinessContext
 */
export interface BusinessContext {
  /** Mode of operation: 'new_startup' or 'existing_business' */
  mode: BusinessMode;
  /** Name of the business or venture */
  business_name: string | null;
  /** Core business concept or value proposition */
  business_idea: string | null;
  /** Detailed overview of operations or offering */
  business_description: string | null;
  /** Industry sector (e.g., FinTech, SaaS, Healthcare) */
  industry: string | null;
  /** Target customer segment or demographic */
  target_market: string | null;
  /** Target geographic region or market */
  geography: string | null;
  /** Monetization approach (e.g., B2B SaaS, Marketplace) */
  business_model: string | null;
  /** Current stage (e.g., Idea, MVP, Seed, Growth) */
  business_stage: string | null;
  /** Primary strategic objective or question to evaluate (required) */
  primary_goal: string;
  /** Available budget for execution/investigation (>= 0) */
  budget: number | null;
  /** Currency code for monetary metrics (default: "INR") */
  currency: string;
  /** Execution/evaluation timeline (e.g., "6 months", "3 years") */
  time_horizon: string | null;
  /** Known operational, legal, or financial constraints */
  constraints: string[];
  /** Pain points or key bottlenecks facing the business */
  current_problems: string[];
  /** Current metrics (e.g., ARR, CAC, LTV, churn) */
  existing_metrics: Record<string, unknown>;
  /** Any additional qualitative context or notes */
  additional_context: string | null;
}

// ---------------------------------------------------------------------------
// AgentPosition
// ---------------------------------------------------------------------------

/** Possible strategic positions a specialist agent can adopt. */
export type PositionType =
  | "recommend"
  | "do_not_recommend"
  | "conditional"
  | "insufficient_evidence";

/**
 * Structured individual claim or assertion made by an agent.
 * Mirrors: backend/app/models/agent.py :: ClaimItem
 */
export interface ClaimItem {
  /** The core assertion made by the agent */
  claim: string;
  /** Supporting evidence for the claim */
  evidence: string | null;
  /** Data source or reference */
  source: string | null;
  /** Underlying assumption supporting the claim */
  assumption: string | null;
  /** Confidence score for this specific claim (0.0 to 1.0) */
  confidence: number;
}

/**
 * Structured position output returned by each specialist agent.
 * Mirrors: backend/app/models/agent.py :: AgentPosition
 */
export interface AgentPosition {
  /** Identifier of the specialist agent (e.g., 'Financial Agent') */
  agent_name: string;
  /** Overall strategic stance or recommendation */
  position: PositionType;
  /** Overall position confidence score (0.0 to 1.0) */
  confidence: number;
  /** Structured claims supporting the position */
  key_claims: ClaimItem[];
  /** Factual evidence items */
  evidence: string[];
  /** Key assumptions relied upon */
  assumptions: string[];
  /** Constraints factored into the analysis */
  constraints_assumed: string[];
  /** Identified risks from the agent's domain perspective */
  risks: string[];
  /** Concrete recommended next steps */
  recommended_actions: string[];
}

/**
 * Records the outcome of a single specialist agent execution during orchestration.
 * Tracks success/failure without fabricating positions on failure.
 * Mirrors: backend/app/models/agent.py :: AgentExecutionRecord
 */
export interface AgentExecutionRecord {
  /** Name of the specialist agent */
  agent_name: string;
  /** True if the agent completed execution without error */
  success: boolean;
  /** Agent's returned position (populated only on success) */
  position: AgentPosition | null;
  /** Error message if the agent failed (populated only on failure) */
  error: string | null;
}

// ---------------------------------------------------------------------------
// Conflict
// ---------------------------------------------------------------------------

/** Categorization of agent disagreements. */
export type ConflictType =
  | "position_conflict"
  | "assumption_conflict"
  | "constraint_conflict"
  | "evidence_conflict"
  | "priority_conflict";

/** Lifecycle status of a detected conflict. */
export type ConflictStatus =
  | "open"
  | "under_review"
  | "resolved"
  | "unresolved"
  | "escalated";

/**
 * Representation of an explicit disagreement detected between two or more agents.
 * Mirrors: backend/app/models/state.py :: Conflict
 */
export interface Conflict {
  /** Unique identifier for the conflict */
  conflict_id: string;
  /** List of agent names involved in the disagreement */
  agents_involved: string[];
  /** Category of the conflict */
  conflict_type: ConflictType;
  /** Detailed description of the disagreement */
  description: string;
  /** Specific claims in opposition */
  conflicting_claims: string[];
  /** Contradictory assumptions identified */
  conflicting_assumptions: string[];
  /** Severity level: 'low' | 'medium' | 'high' | 'critical' */
  severity: string;
  /** Current resolution status */
  status: ConflictStatus;
  /** Summary of how the conflict was resolved (null if unresolved) */
  resolution: string | null;
  /** Evidence used during conflict evaluation */
  supporting_evidence: string[];
}

// ---------------------------------------------------------------------------
// NegotiationRound
// ---------------------------------------------------------------------------

/**
 * Record of a single negotiation round between conflicting agents.
 * Preserves history of how agents adapted their positions over time.
 * Mirrors: backend/app/models/state.py :: NegotiationRound
 */
export interface NegotiationRound {
  /** Sequential round number of negotiation (>= 1) */
  round_number: number;
  /** Agents participating in this round */
  participants: string[];
  /** The core issue or conflict being negotiated */
  issue: string;
  /** Agent positions prior to round */
  previous_positions: AgentPosition[];
  /** New evidence introduced during round */
  evidence_exchanged: string[];
  /** Counterarguments presented by agents */
  arguments: string[];
  /** Updated agent positions post-round */
  revised_positions: AgentPosition[];
  /** Resolution achieved in this round, if any */
  resolution: string | null;
  /** Points that remain contentious */
  unresolved_points: string[];
}

// ---------------------------------------------------------------------------
// FinalDecision
// ---------------------------------------------------------------------------

/**
 * Synthesized final decision produced by Orchestrator / Synthesis Agent.
 * Mirrors: backend/app/models/state.py :: FinalDecision
 *
 * Note: `confidence` is an aggregate analytical indicator reflecting the degree
 * of certainty across the agent collaboration. It does NOT represent a
 * probability of business success or startup viability.
 */
export interface FinalDecision {
  /** Final strategic recommendation */
  recommendation: PositionType;
  /** Comprehensive executive summary and justification */
  rationale: string;
  /**
   * Aggregate analytical confidence indicator (0.0 to 1.0).
   * Reflects analytical certainty across the collaboration — NOT a probability
   * of business success.
   */
  confidence: number;
  /** Primary drivers influencing the recommendation */
  key_factors: string[];
  /** Alternative strategic paths evaluated */
  alternatives_considered: string[];
  /** Key strategic or financial trade-offs accepted */
  trade_offs: string[];
  /** Critical risks and mitigation strategies */
  risks: string[];
  /** Core assumptions underlying the final decision */
  assumptions: string[];
  /** Preserved minority agent dissent or concerns */
  unresolved_dissent: string[];
  /** Sequential action items for execution */
  action_plan: string[];
  /** Traceability links to supporting agent evidence */
  evidence_trace: string[];
}

// ---------------------------------------------------------------------------
// SharedBusinessState
// ---------------------------------------------------------------------------

/** Overall execution status of the shared business state. */
export type StateStatus =
  | "initialized"
  | "analyzing"
  | "conflict_detected"
  | "negotiating"
  | "consensus_reached"
  | "human_review_required"
  | "completed";

/**
 * Central canonical state — the full output of POST /api/orchestrate.
 * Contains the complete collaboration trace including all agent positions,
 * conflicts, negotiation history, revised positions, and the final decision.
 * Mirrors: backend/app/models/state.py :: SharedBusinessState
 */
export interface SharedBusinessState {
  /** Unique execution or session identifier */
  run_id: string;
  /** Initial input business parameters */
  business_context: BusinessContext;
  /** Verified facts established across agents */
  canonical_facts: string[];
  /** Active business and operational constraints */
  constraints: string[];
  /** Global and agent-specific working assumptions */
  assumptions: string[];
  /** Unresolved questions requiring further data */
  open_questions: string[];
  /** Original specialist agent positions (never overwritten post-negotiation) */
  agent_positions: AgentPosition[];
  /** Active or historical conflicts detected */
  conflicts: Conflict[];
  /** Log of negotiation iterations */
  negotiation_history: NegotiationRound[];
  /** Latest revised agent positions post-negotiation */
  revised_positions: AgentPosition[];
  /** Final synthesized decision output (null until synthesis node runs) */
  final_decision: FinalDecision | null;
  /** Current workflow state */
  status: StateStatus;
  /** Per-agent success/failure record from the orchestration run */
  execution_log: AgentExecutionRecord[];
}
