from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Test GET /api/health returns 200 and status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_model_example_endpoint_default():
    """Test GET /api/business/model-example default returns new_startup mode example."""
    response = client.get("/api/business/model-example")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "new_startup"
    assert data["business_name"] == "EcoClean Tech"
    assert "primary_goal" in data


def test_model_example_endpoint_existing_business():
    """Test GET /api/business/model-example with mode=existing_business."""
    response = client.get("/api/business/model-example?mode=existing_business")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "existing_business"
    assert data["business_name"] == "Acme Logistics Inc."


def test_validate_new_startup():
    """Test POST /api/business/validate with a valid new startup payload."""
    payload = {
        "mode": "new_startup",
        "business_name": "HealthPulse AI",
        "business_idea": "AI diagnostics assistant for primary clinics",
        "industry": "HealthTech",
        "primary_goal": "Assess market potential and regulatory barriers",
        "budget": 2000000.0,
        "currency": "INR",
        "constraints": ["ISO 27001 compliance"],
    }
    response = client.post("/api/business/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "new_startup"
    assert data["business_name"] == "HealthPulse AI"
    assert data["budget"] == 2000000.0


def test_validate_existing_business():
    """Test POST /api/business/validate with a valid existing business payload."""
    payload = {
        "mode": "existing_business",
        "business_name": "RetailFlow Systems",
        "industry": "Retail & Software",
        "primary_goal": "Evaluate pivot to SaaS pricing model",
        "budget": 10000000.0,
        "current_problems": ["High churn rate among SMB tier"],
        "existing_metrics": {"ARR": "50,000,000 INR", "churn_rate": "4.2%"},
    }
    response = client.post("/api/business/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "existing_business"
    assert data["business_name"] == "RetailFlow Systems"
    assert data["existing_metrics"]["churn_rate"] == "4.2%"


def test_validate_invalid_payload():
    """Test POST /api/business/validate with missing required fields or invalid mode."""
    # Missing required 'primary_goal' and 'mode'
    payload = {
        "business_name": "Incomplete Payload",
    }
    response = client.post("/api/business/validate", json=payload)
    assert response.status_code == 422

    # Invalid mode string
    payload_invalid_mode = {
        "mode": "invalid_mode_type",
        "primary_goal": "Test invalid mode",
    }
    response_invalid_mode = client.post("/api/business/validate", json=payload_invalid_mode)
    assert response_invalid_mode.status_code == 422


def test_initialize_shared_goal_endpoint_new_startup():
    """Test POST /api/coordination/shared-goal/initialize with new startup payload."""
    payload = {
        "mode": "new_startup",
        "business_name": "HealthPulse AI",
        "industry": "HealthTech",
        "primary_goal": "Validate market entrance",
        "budget": 2000000.0,
    }
    response = client.post("/api/coordination/shared-goal/initialize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["run_id"].startswith("run-")
    assert data["status"] == "initialized"
    assert data["business_context"]["business_name"] == "HealthPulse AI"
    assert len(data["canonical_facts"]) > 0


def test_initialize_shared_goal_endpoint_existing_business():
    """Test POST /api/coordination/shared-goal/initialize with existing business payload."""
    payload = {
        "mode": "existing_business",
        "business_name": "Acme Freight",
        "industry": "Logistics",
        "primary_goal": "Evaluate cold-chain expansion",
        "existing_metrics": {"ARR": "15M INR"},
    }
    response = client.post("/api/coordination/shared-goal/initialize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["run_id"].startswith("run-")
    assert data["status"] == "initialized"
    assert data["business_context"]["business_name"] == "Acme Freight"


def test_validate_shared_goal_state_endpoint():
    """Test POST /api/coordination/shared-goal/validate endpoint."""
    # First initialize state
    payload = {
        "mode": "new_startup",
        "primary_goal": "Validation state test",
    }
    init_res = client.post("/api/coordination/shared-goal/initialize", json=payload)
    state_json = init_res.json()

    # Validate state
    val_res = client.post("/api/coordination/shared-goal/validate", json=state_json)
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["valid"] is True
    assert len(val_data["errors"]) == 0
    assert val_data["run_id"] == state_json["run_id"]


def test_detect_conflicts_endpoint():
    """Test POST /api/coordination/conflicts/detect endpoint."""
    init_res = client.post("/api/coordination/shared-goal/initialize", json={
        "mode": "new_startup",
        "primary_goal": "Conflict Detection API Test",
    })
    state_json = init_res.json()

    pos1 = {
        "agent_name": "Financial Agent",
        "position": "do_not_recommend",
        "confidence": 0.9,
    }
    pos2 = {
        "agent_name": "Market Research Agent",
        "position": "recommend",
        "confidence": 0.85,
    }

    payload = {
        "state": state_json,
        "positions": [pos1, pos2],
    }

    response = client.post("/api/coordination/conflicts/detect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0
    assert data["status"] == "conflict_detected"
    assert len(data["conflicts"]) > 0
    assert data["state"]["status"] == "conflict_detected"


def test_run_negotiation_endpoint():
    """Test POST /api/coordination/negotiation/run endpoint."""
    init_res = client.post("/api/coordination/shared-goal/initialize", json={
        "mode": "new_startup",
        "primary_goal": "Negotiation Endpoint Test",
    })
    state_json = init_res.json()

    pos1 = {
        "agent_name": "Financial Agent",
        "position": "do_not_recommend",
        "confidence": 0.9,
        "evidence": ["CapEx limit exceeded."],
    }
    pos2 = {
        "agent_name": "Market Research Agent",
        "position": "recommend",
        "confidence": 0.85,
        "evidence": ["Phased pilot rollout proposed."],
    }

    detect_res = client.post("/api/coordination/conflicts/detect", json={
        "state": state_json,
        "positions": [pos1, pos2],
    })
    detect_data = detect_res.json()

    neg_payload = {
        "state": detect_data["state"],
        "positions": [pos1, pos2],
        "conflicts": detect_data["conflicts"],
    }

    response = client.post("/api/coordination/negotiation/run", json=neg_payload)
    assert response.status_code == 200
    data = response.json()
    assert "state" in data
    assert "negotiation_rounds" in data
    assert len(data["negotiation_rounds"]) > 0
    assert data["resolved_conflicts"] + data["unresolved_conflicts"] == len(detect_data["conflicts"])



