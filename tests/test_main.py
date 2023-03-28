import os

from fastapi.testclient import TestClient

from main import app
import pytest


client = TestClient(app)


# i know, hooks in pytest exist, but for some reason they don't work
@pytest.fixture(scope="session", autouse=True)
def session_teardown():
    yield
    for file in os.listdir("media"):
        if file == '1.mp4':
            continue
        os.remove(os.path.join("media", file))


def test_stream_video():
    response = client.get("/start_streaming/1.mp4")
    assert response.status_code == 200


def test_next_frames_generation():
    response = client.get("/start_streaming/1.mp4")
    next_frame_link = response.json()["start_filename"]

    for _ in range(5):
        response = client.get(f"/video_part/{next_frame_link}")
        next_frame_link = response.headers["x-next-frame"]
