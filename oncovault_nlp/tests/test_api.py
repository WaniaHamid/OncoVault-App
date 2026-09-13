import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_extract_endpoint():
    payload = {"text": "Patient has persistent fatigue and fever but denies bone pain. WBC is 14.5 k/uL."}
    response = client.post("/extract", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "symptoms" in data
    assert data["symptoms"]["persistentWeaknessAndFatigue"]["value"] is True
    assert data["symptoms"]["bonePain"]["value"] is False
    assert data["cbc"]["wbc"]["value"] == 14.5
