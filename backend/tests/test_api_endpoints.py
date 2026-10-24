from fastapi.testclient import TestClient
from app.server import app

def test_health():
    r=TestClient(app).get("/health")
    assert r.status_code==200
    assert r.json()["status"]=="ok"

def test_screenshot_requires_admin():
    r=TestClient(app).post("/api/screenshots/preview",data={"game_id":"1"},files={"file":("a.png",b"not-a-real-image","image/png")})
    assert r.status_code==401
