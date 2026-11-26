from fastapi.testclient import TestClient

from recoverwell.api import app

client = TestClient(app)
BODY = dict(request_id="r1", user_id="u1", mood=3, energy=3, stress=4, sleep_hours=6.5,
            free_minutes=10, hour=14)


def test_recommend_then_feedback():
    r = client.post("/recommend", json=BODY)
    assert r.status_code == 200 and r.json()["duration_min"] <= 10
    f = client.post("/feedback", json=dict(request_id="r1", activity_id=r.json()["activity_id"], completed=True))
    assert f.json()["updated"] is True
