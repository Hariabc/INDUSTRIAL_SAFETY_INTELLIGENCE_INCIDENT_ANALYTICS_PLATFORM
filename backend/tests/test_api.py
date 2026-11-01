from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_dashboard_overview(client: TestClient):
    r = client.get("/api/dashboard/overview")
    assert r.status_code == 200
    data = r.json()
    assert "stats" in data
    assert data["stats"]["total_plants"] == 4
    assert data["stats"]["total_machines"] == 60
    assert data["stats"]["total_alarms"] >= 50000
    assert len(data["recent_critical_alarms"]) > 0


def test_plants_endpoints(client: TestClient):
    # List
    r = client.get("/api/plants")
    assert r.status_code == 200
    plants = r.json()
    assert len(plants) == 4

    # Detail
    plant_id = plants[0]["id"]
    r_det = client.get(f"/api/plants/{plant_id}")
    assert r_det.status_code == 200
    det = r_det.json()
    assert det["plant"]["id"] == plant_id
    assert len(det["machines"]) > 0
    assert len(det["safety_zones"]) > 0


def test_machines_endpoints(client: TestClient):
    # List with pagination
    r = client.get("/api/machines?page=1&page_size=10")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 60
    assert len(data["items"]) == 10

    # Search
    r_search = client.get("/api/machines?search=MCH-001")
    assert r_search.status_code == 200
    assert len(r_search.json()["items"]) >= 1

    # Detail
    m_id = data["items"][0]["id"]
    r_det = client.get(f"/api/machines/{m_id}")
    assert r_det.status_code == 200
    det = r_det.json()
    assert det["machine"]["id"] == m_id
    assert len(det["interlocks"]) >= 3

    # History
    r_hist = client.get(f"/api/machines/{m_id}/history")
    assert r_hist.status_code == 200
    hist = r_hist.json()
    assert len(hist["state_transitions"]) > 0


def test_alarms_endpoints(client: TestClient):
    r = client.get("/api/alarms?page=1&page_size=20&severity=CRITICAL")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 20
    assert all(a["severity"] == "CRITICAL" for a in data["items"])

    # Detail
    alm_id = data["items"][0]["id"]
    r_det = client.get(f"/api/alarms/{alm_id}")
    assert r_det.status_code == 200
    det = r_det.json()
    assert det["alarm"]["id"] == alm_id
    assert "definition" in det
    assert "machine" in det


def test_incidents_and_authentic_timeline(client: TestClient):
    r = client.get("/api/incidents?page=1&page_size=5")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 5

    inc_id = data["items"][0]["id"]
    r_det = client.get(f"/api/incidents/{inc_id}")
    assert r_det.status_code == 200
    det = r_det.json()
    assert det["incident"]["id"] == inc_id
    assert "timeline" in det
    assert len(det["timeline"]) > 0

    # Verify timeline is ordered chronologically
    timestamps = [t["timestamp"] for t in det["timeline"]]
    assert timestamps == sorted(timestamps), "Timeline must be strictly chronological"


def test_corrective_action_verification_rules(client: TestClient):
    r = client.get("/api/corrective-actions?page=1&page_size=10")
    assert r.status_code == 200
    actions = r.json()["items"]
    assert len(actions) > 0

    # Find an action to test verification rule
    target_act = actions[0]
    act_id = target_act["id"]

    # Verify action
    r_verify = client.post(
        f"/api/corrective-actions/{act_id}/verify",
        json={
            "verified_by": "Safety Officer Chief",
            "verification_notes": "Passed comprehensive safety review."
        }
    )
    assert r_verify.status_code == 200
    assert r_verify.json()["is_verified"] is True


def test_prevent_closing_unverified_action(client: TestClient):
    """Business Rule: Cannot close an unverified action without verification."""
    # Create an unverified action
    r_inc = client.get("/api/incidents?page=1&page_size=1")
    inc_id = r_inc.json()["items"][0]["id"]

    r_create = client.post(
        "/api/corrective-actions",
        json={
            "incident_id": inc_id,
            "title": "Unverified Test Work Order",
            "assigned_to": "Field Tech",
            "priority": "HIGH",
            "due_date": "2026-11-15T00:00:00"
        }
    )
    assert r_create.status_code == 200
    act_id = r_create.json()["id"]

    # Attempt to close without verification -> MUST fail with 400
    r_close = client.put(
        f"/api/corrective-actions/{act_id}/status",
        json={"status": "CLOSED", "actor": "Test Tech"}
    )
    assert r_close.status_code == 400
    assert "requires mandatory physical verification" in r_close.json()["detail"]


def test_analytics_endpoints(client: TestClient):
    r_trends = client.get("/api/analytics/alarm-trends")
    assert r_trends.status_code == 200
    assert len(r_trends.json()) > 0

    r_sev = client.get("/api/analytics/severity-distribution")
    assert r_sev.status_code == 200
    assert len(r_sev.json()) >= 4

    r_unsafe = client.get("/api/analytics/unsafe-machines")
    assert r_unsafe.status_code == 200
    assert len(r_unsafe.json()) > 0

    r_eval = client.get("/api/analytics/model-evaluation")
    assert r_eval.status_code == 200
    assert "model_performance" in r_eval.json()
    assert "operational_kpis" in r_eval.json()


def test_data_quality_endpoint(client: TestClient):
    r = client.get("/api/data-quality")
    assert r.status_code == 200
    assert "summary" in r.json()
    assert r.json()["summary"]["overall_status"] == "PASSED"


def test_export_endpoint(client: TestClient):
    r = client.get("/api/export/plants?format=csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert len(r.text) > 0
