from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

endpoints = [
    "/api/agents/market-research/analyze",
    "/api/agents/financial/analyze",
    "/api/agents/competition/analyze",
    "/api/agents/customer/analyze",
    "/api/agents/marketing/analyze",
    "/api/agents/operations/analyze",
    "/api/agents/risk-regulatory/analyze",
]

r_startup = client.get("/api/business/model-example?mode=new_startup").json()
r_existing = client.get("/api/business/model-example?mode=existing_business").json()

print("=== STARTUP MODE ANALYSIS CHECKS ===")
for ep in endpoints:
    r = client.post(ep, json=r_startup)
    res = r.json()
    print(f"{ep} -> HTTP {r.status_code} | Agent: {res['agent_name']} | Stance: {res['position']} | Confidence: {res['confidence']}")

print("\n=== EXISTING BUSINESS MODE ANALYSIS CHECKS ===")
for ep in endpoints:
    r = client.post(ep, json=r_existing)
    res = r.json()
    print(f"{ep} -> HTTP {r.status_code} | Agent: {res['agent_name']} | Stance: {res['position']} | Confidence: {res['confidence']}")
