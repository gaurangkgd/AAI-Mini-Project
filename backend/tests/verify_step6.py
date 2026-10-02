import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- 1. Initialize State ---")
ctx = {
    "mode": "new_startup",
    "business_name": "ConflictDemo Startup",
    "primary_goal": "Assess market launch feasibility",
    "constraints": ["Max budget limit of 15 Lakhs"],
}
init_res = client.post("/api/coordination/shared-goal/initialize", json=ctx)
state_json = init_res.json()
print("Run ID:", state_json["run_id"])
print("Initial Status:", state_json["status"])

print("\n--- 2. Create Opposing Specialist Positions ---")
pos_mkt = {
    "agent_name": "Market Research Agent",
    "position": "recommend",
    "confidence": 0.85,
    "key_claims": [{"claim": "Validated strong demand in renewable sector.", "confidence": 0.85}],
    "assumptions": ["Capital budget is sufficient for launch."],
    "constraints_assumed": ["Max budget limit of 15 Lakhs"],
    "evidence": ["High TAM growth."],
}

pos_fin = {
    "agent_name": "Financial Agent",
    "position": "do_not_recommend",
    "confidence": 0.90,
    "key_claims": [{"claim": "Missing customer demand validation in target segment.", "confidence": 0.90}],
    "assumptions": ["Capital budget is insufficient for logistics fleet."],
    "constraints_assumed": ["Capital expenditure exceeds budget limit"],
    "evidence": ["Burn rate exceeds capital runway."],
}

print("\n--- 3. Detect Conflicts API (POST /api/coordination/conflicts/detect) ---")
payload = {
    "state": state_json,
    "positions": [pos_mkt, pos_fin],
}
detect_res = client.post("/api/coordination/conflicts/detect", json=payload)
print("HTTP Status:", detect_res.status_code)
resp_data = detect_res.json()
print("Conflict Count:", resp_data["count"])
print("Updated State Status:", resp_data["status"])
print("\nDetected Conflicts Breakdown:")
for cnf in resp_data["conflicts"]:
    print(f" - [{cnf['severity'].upper()}] {cnf['conflict_type']} between {cnf['agents_involved']}: {cnf['description']}")
