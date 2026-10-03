from fastapi.testclient import TestClient
from gitops.main import app

def test_drift_is_reported_and_not_applied():
    client = TestClient(app)
    drifted = client.post("/compare", json={"desired": {"image": "billing:1.4.2", "replicas": 2}, "observed": {"image": "billing:1.4.2", "replicas": 5}}).json()
    assert drifted["drifted"] is True
    assert drifted["diffs"] == ["replicas"]
    assert drifted["applied"] is False
    matched = client.post("/compare", json={"desired": {"image": "billing:1.4.2", "replicas": 2}, "observed": {"image": "billing:1.4.2", "replicas": 2}}).json()
    assert matched["drifted"] is False
