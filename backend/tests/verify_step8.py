"""
verify_step8.py — Visual trace script for Step 8 orchestration pipeline.

Runs a full end-to-end orchestration call via FastAPI TestClient and
prints the complete collaboration trace for manual inspection.

Run with:
    cd backend
    .venv\\Scripts\\python.exe tests/verify_step8.py
"""

import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

DIVIDER = "=" * 70

def section(title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


# ---------------------------------------------------------------------------
# SCENARIO 1: New Startup — Well-formed input
# ---------------------------------------------------------------------------
section("SCENARIO 1: NEW STARTUP — EcoClean Tech")

payload_startup = {
    "mode": "new_startup",
    "business_name": "EcoClean Tech",
    "business_idea": "AI-driven waterless solar panel cleaning drone system",
    "business_description": "Automated robotics solution to clean utility-scale solar farms without water",
    "industry": "CleanTech / Renewable Energy",
    "target_market": "Utility-Scale Solar Farm Operators",
    "geography": "Rajasthan & Gujarat, India",
    "business_model": "Robotics-as-a-Service (RaaS) subscription",
    "business_stage": "Idea / Pre-seed",
    "primary_goal": "Validate market feasibility, financial viability, and operational constraints",
    "budget": 1500000.0,
    "currency": "INR",
    "time_horizon": "6 months",
    "constraints": [
        "Bootstrapped pre-seed capital limit of 15 Lakhs INR",
        "Must comply with Indian drone regulatory framework (DGCA)",
    ],
    "current_problems": [
        "Lack of field testing data under extreme desert conditions",
        "High customer acquisition lead times in utility sector",
    ],
    "existing_metrics": {},
    "additional_context": "Founders have 5 years experience in robotics and power grid operations.",
}

resp1 = client.post("/api/orchestrate", json=payload_startup)
assert resp1.status_code == 200, f"HTTP {resp1.status_code}: {resp1.text}"
s1 = resp1.json()

print(f"\nRun ID         : {s1['run_id']}")
print(f"Final Status   : {s1['status']}")

print(f"\n--- Execution Log ({len(s1['execution_log'])} agents) ---")
for rec in s1["execution_log"]:
    status_str = "OK" if rec["success"] else f"FAILED: {rec.get('error', '')}"
    pos_str = rec["position"]["position"] if rec.get("position") else "N/A"
    conf_str = f"{rec['position']['confidence']:.2f}" if rec.get("position") else "N/A"
    print(f"  [{status_str:8s}] {rec['agent_name']:35s} | pos={pos_str:25s} | conf={conf_str}")

print(f"\n--- Original Agent Positions ({len(s1['agent_positions'])}) ---")
for pos in s1["agent_positions"]:
    print(f"  {pos['agent_name']:35s} | {pos['position']:25s} | conf={pos['confidence']:.2f}")

print(f"\n--- Conflicts Detected: {len(s1['conflicts'])} ---")
for c in s1["conflicts"]:
    print(f"  [{c['severity'].upper():8s}] {c['status']:12s} | {c['conflict_type']:25s} | {c['description'][:60]}...")

print(f"\n--- Negotiation Rounds: {len(s1['negotiation_history'])} ---")
for rnd in s1["negotiation_history"]:
    print(f"  Round {rnd['round_number']}: {rnd['issue'][:60]}")
    print(f"    Resolution : {rnd['resolution'] or 'None'}")
    print(f"    Unresolved : {rnd['unresolved_points']}")

print(f"\n--- Revised Positions: {len(s1['revised_positions'])} ---")
for pos in s1["revised_positions"]:
    print(f"  {pos['agent_name']:35s} | {pos['position']:25s} | conf={pos['confidence']:.2f}")

fd1 = s1["final_decision"]
print(f"\n--- FINAL DECISION ---")
print(f"  Recommendation : {fd1['recommendation']}")
print(f"  Confidence     : {fd1['confidence']:.3f}  (aggregate analytical indicator — NOT a probability of business success)")
print(f"  Rationale      : {fd1['rationale'][:120]}...")
print(f"  Key Factors    : {len(fd1['key_factors'])} items")
for kf in fd1["key_factors"][:3]:
    print(f"    - {kf[:80]}")
print(f"  Risks          : {len(fd1['risks'])} items")
print(f"  Action Plan    : {len(fd1['action_plan'])} items")
for ap in fd1["action_plan"][:3]:
    print(f"    -> {ap[:80]}")
print(f"  Evidence Trace : {len(fd1['evidence_trace'])} items")
print(f"  Trade-offs     : {len(fd1['trade_offs'])} items")
print(f"  Unresolved Dissent : {len(fd1['unresolved_dissent'])} items")
for ud in fd1["unresolved_dissent"][:2]:
    print(f"    [!] {ud[:80]}")


# ---------------------------------------------------------------------------
# SCENARIO 2: Existing Business — Strategic expansion decision
# ---------------------------------------------------------------------------
section("SCENARIO 2: EXISTING BUSINESS — Acme Logistics Inc.")

payload_existing = {
    "mode": "existing_business",
    "business_name": "Acme Logistics Inc.",
    "business_description": "Mid-sized regional logistics and freight forwarding company",
    "industry": "Logistics & Supply Chain",
    "target_market": "B2B E-commerce & Manufacturing",
    "geography": "India (Tier 1 & Tier 2 Cities)",
    "business_model": "B2B Service Fee & Subscription",
    "business_stage": "Growth / Expansion",
    "primary_goal": "Evaluate expansion into cold-chain warehouse automation",
    "budget": 5000000.0,
    "currency": "INR",
    "time_horizon": "12 months",
    "constraints": [
        "Regulatory approval required for cold storage infrastructure",
        "Max debt financing capped at 40% of expansion budget",
    ],
    "current_problems": [
        "Rising fuel costs impacting margins by 8%",
        "Warehouse utilization currently bottlenecked at 82%",
    ],
    "existing_metrics": {
        "ARR": "12,000,000 INR",
        "EBITDA_margin": "14%",
        "fleet_count": 45,
    },
    "additional_context": "Board requires strategic risk-benefit analysis before Q3 capital allocation.",
}

resp2 = client.post("/api/orchestrate", json=payload_existing)
assert resp2.status_code == 200, f"HTTP {resp2.status_code}: {resp2.text}"
s2 = resp2.json()

print(f"\nRun ID         : {s2['run_id']}")
print(f"Final Status   : {s2['status']}")

fd2 = s2["final_decision"]
print(f"\n--- FINAL DECISION ---")
print(f"  Recommendation : {fd2['recommendation']}")
print(f"  Confidence     : {fd2['confidence']:.3f}")
print(f"  Rationale      : {fd2['rationale'][:120]}...")
print(f"  Risks          : {len(fd2['risks'])} items")
print(f"  Action Plan    : {len(fd2['action_plan'])} items")
print(f"  Unresolved Dissent : {len(fd2['unresolved_dissent'])} items")


# ---------------------------------------------------------------------------
# SCENARIO 3: Minimal Input — Robustness check
# ---------------------------------------------------------------------------
section("SCENARIO 3: MINIMAL INPUT — Robustness")

payload_minimal = {
    "mode": "new_startup",
    "primary_goal": "Assess viability of a new product idea",
}

resp3 = client.post("/api/orchestrate", json=payload_minimal)
assert resp3.status_code == 200, f"HTTP {resp3.status_code}: {resp3.text}"
s3 = resp3.json()

fd3 = s3["final_decision"]
print(f"\nRun ID         : {s3['run_id']}")
print(f"Final Status   : {s3['status']}")
print(f"Recommendation : {fd3['recommendation']}")
print(f"Confidence     : {fd3['confidence']:.3f}")
print(f"Agent Positions: {len(s3['agent_positions'])}")
print(f"Execution Log  : {len(s3['execution_log'])} records")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
section("STEP 8 VERIFICATION COMPLETE")
print("\n[OK] Scenario 1 (New Startup)       - Pipeline completed")
print(f"     Recommendation: {s1['final_decision']['recommendation']}")
print(f"     Confidence    : {s1['final_decision']['confidence']:.3f}")
print(f"     Conflicts     : {len(s1['conflicts'])}")
print(f"     Negotiation   : {len(s1['negotiation_history'])} round(s)")

print("\n[OK] Scenario 2 (Existing Business) - Pipeline completed")
print(f"     Recommendation: {s2['final_decision']['recommendation']}")
print(f"     Confidence    : {s2['final_decision']['confidence']:.3f}")
print(f"     Conflicts     : {len(s2['conflicts'])}")

print("\n[OK] Scenario 3 (Minimal Input)     - No crash, pipeline completed")
print(f"     Recommendation: {s3['final_decision']['recommendation']}")

print(f"\nAll 3 scenarios passed the Step 8 visual verification.\n")
