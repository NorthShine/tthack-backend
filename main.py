import time
import typing
import uuid

import cv2
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from vidgear.gears import CamGear, StreamGear, VideoGear, WriteGear

app = FastAPI()
stream = VideoGear(source="media/1.mp4").start()
output_params = {"-fourcc": "MJPG", "-fps": 30}
queue = []


def video_generator():
    frame_rate = 60
    while True:
        frame = stream.read()
        if frame is None:
            break

        random_filename = uuid.uuid4()
        writer = WriteGear(f"media/{random_filename}.mp4", compression_mode=False, **output_params)
        print(random_filename)
        queue.append(random_filename)        
        for _ in range(frame_rate * 2):
            writer.write(frame)
            frame = stream.read()
        writer.close()
        yield random_filename

generator = video_generator()


@app.get('/video_part/{video_filename}/')
async def get_video_filename(video_filename: str):
    try:
        next_filename = next(generator)
    except StopIteration:
        return {"detail": "stream_finished"}

    def iterfile():
        with open(f"media/{video_filename}", mode="rb") as file_like:
            yield from file_like
    headers = {
        "Next-Part": str(next_filename)
    }
    return StreamingResponse(iterfile(), media_type="video/mp4", headers=headers)


@app.get('/start_streaming/')
async def video_feed():
    current_filename = next(generator)
    return {'start_filename': current_filename}

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=5000, access_log=False)
