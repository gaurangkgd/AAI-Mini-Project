import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=== SCENARIO 1: RESOLVABLE CONFLICT NEGOTIATION ===")
init_res1 = client.post("/api/coordination/shared-goal/initialize", json={
    "mode": "new_startup",
    "business_name": "EcoClean Tech",
    "primary_goal": "Assess market launch feasibility",
    "budget": 1500000.0,
})
state1 = init_res1.json()

pos_mkt_res = {
    "agent_name": "Market Research Agent",
    "position": "recommend",
    "confidence": 0.85,
    "evidence": ["Phased pilot rollout proposed to cap initial expenditure."],
    "recommended_actions": ["Run phased pilot rollout with 15 solar operators."],
}
pos_fin_res = {
    "agent_name": "Financial Agent",
    "position": "do_not_recommend",
    "confidence": 0.90,
    "evidence": ["CapEx limits exceeded."],
    "assumptions": ["Burn rate is unsustainable."],
}

detect_res1 = client.post("/api/coordination/conflicts/detect", json={
    "state": state1,
    "positions": [pos_mkt_res, pos_fin_res],
}).json()

print(f"Conflicts Detected: {detect_res1['count']} | State Status: {detect_res1['status']}")

neg_res1 = client.post("/api/coordination/negotiation/run", json={
    "state": detect_res1["state"],
    "positions": [pos_mkt_res, pos_fin_res],
    "conflicts": detect_res1["conflicts"],
}).json()

print("Negotiation Endpoint HTTP 200")
print(f"Resolved Conflicts: {neg_res1['resolved_conflicts']} | Unresolved Conflicts: {neg_res1['unresolved_conflicts']}")
print("Final State Status:", neg_res1["state"]["status"])
print("Revised Positions Count:", len(neg_res1["state"]["revised_positions"]))
for r_pos in neg_res1["state"]["revised_positions"]:
    print(f" - Agent: {r_pos['agent_name']} | Revised Position: {r_pos['position']} | Conf: {r_pos['confidence']}")


print("\n=== SCENARIO 2: UNRESOLVED CONFLICT DISSENT PRESERVATION ===")
init_res2 = client.post("/api/coordination/shared-goal/initialize", json={
    "mode": "new_startup",
    "business_name": "HighRisk Venture",
    "primary_goal": "Assess aggressive growth",
})
state2 = init_res2.json()

pos_mkt_unres = {
    "agent_name": "Market Research Agent",
    "position": "recommend",
    "confidence": 0.95,
    "evidence": ["Massive market demand."],
}
pos_fin_unres = {
    "agent_name": "Financial Agent",
    "position": "do_not_recommend",
    "confidence": 0.95,
    "evidence": ["Zero cash runway and extreme default risk."],
}

unres_conflict = {
    "conflict_id": "cnf-unresolvable-001",
    "agents_involved": ["Market Research Agent", "Financial Agent"],
    "conflict_type": "position_conflict",
    "description": "Irreconcilable divergence on default risk vs market demand",
    "conflicting_claims": ["Demand is massive", "Cash runway is zero"],
    "conflicting_assumptions": [],
    "severity": "high",
    "status": "open",
    "supporting_evidence": [],
}

neg_res2 = client.post("/api/coordination/negotiation/run", json={
    "state": state2,
    "positions": [pos_mkt_unres, pos_fin_unres],
    "conflicts": [unres_conflict],
}).json()

print(f"Resolved Conflicts: {neg_res2['resolved_conflicts']} | Unresolved Conflicts: {neg_res2['unresolved_conflicts']}")
print("Final State Status:", neg_res2["state"]["status"])
print("Unresolved Points Recorded:", neg_res2["negotiation_rounds"][0]["unresolved_points"])
