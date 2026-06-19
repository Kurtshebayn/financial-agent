from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_422_endpoint():
    response = client.post("/summarize", json={"text": "texto corto"})
    body = response.json()
    assert body["detail"][0]["type"] == "string_too_short"
