import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- 1. GET /api/health ---")
r_health = client.get("/api/health")
print("Status:", r_health.status_code, r_health.json())

print("\n--- 2. GET /api/business/model-example (startup) ---")
r_ex_startup = client.get("/api/business/model-example?mode=new_startup").json()

print("\n--- 3. POST /api/coordination/shared-goal/initialize (new_startup) ---")
r_init_startup = client.post("/api/coordination/shared-goal/initialize", json=r_ex_startup)
print("Status:", r_init_startup.status_code)
state_startup = r_init_startup.json()
print("Run ID:", state_startup["run_id"])
print("Status:", state_startup["status"])
print("Canonical Facts Count:", len(state_startup["canonical_facts"]))
print("Canonical Facts Sample:", state_startup["canonical_facts"][:3])
print("Assumptions:", state_startup["assumptions"])
print("Open Questions:", state_startup["open_questions"])

print("\n--- 4. POST /api/coordination/shared-goal/initialize (existing_business) ---")
r_ex_biz = client.get("/api/business/model-example?mode=existing_business").json()
r_init_biz = client.post("/api/coordination/shared-goal/initialize", json=r_ex_biz)
print("Status:", r_init_biz.status_code)
state_biz = r_init_biz.json()
print("Run ID:", state_biz["run_id"])
print("Canonical Facts Sample:", state_biz["canonical_facts"][:3])

print("\n--- 5. POST /api/coordination/shared-goal/validate ---")
r_val = client.post("/api/coordination/shared-goal/validate", json=state_biz)
print("Status:", r_val.status_code, r_val.json())
