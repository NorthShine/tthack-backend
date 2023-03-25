from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_stream_video():
    headers = {
        "range": "bytes=0-"
    }
    response = client.get("/stream/1.mp4", headers=headers)
    assert response.status_code == 206
