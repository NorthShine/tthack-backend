import time
import typing
import uuid
import os
from pathlib import Path

import cv2
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from vidgear.gears import CamGear, StreamGear, VideoGear, WriteGear

app = FastAPI()
stream = VideoGear(source="media/1.mp4").start()
output_params = {"-fourcc": "mp4v", "-fps": 30}
queue = []

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def video_generator():
    frame_rate = 60
    while True:
        frame = stream.read()
        frame_shape = frame.shape
        frame_width = frame_shape[1]
        frame_height = frame_shape[0]
        if frame is None:
            break

        random_filename = uuid.uuid4()
        # writer = WriteGear(f"media/{random_filename}.mp4", compression_mode=False, **output_params)
        writer = cv2.VideoWriter(
            f"media/{random_filename}.mp4",
            cv2.VideoWriter_fourcc(*'mp4v'),
            30,
            (frame_width, frame_height)
        )
        print(random_filename)
        queue.append(random_filename)        
        for _ in range(frame_rate * 2):
            writer.write(frame)
            frame = stream.read()
        writer.release()
        yield random_filename

generator = video_generator()


@app.get('/video_part/{video_filename}/')
async def get_video_filename(request: Request, video_filename: str):
    video_filename = f"media/{video_filename}"
    return FileResponse(video_filename, media_type="video/mp4")


@app.get('/start_streaming/')
async def video_feed():
    current_filename = next(generator)
    return {'start_filename': current_filename}


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=5000, access_log=False)
