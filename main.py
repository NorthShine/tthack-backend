import subprocess
import typing
import uuid

import cv2
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from vidgear.gears import VideoGear

app = FastAPI()
output_params = {"-fourcc": "mp4v", "-fps": 30}
queue = {}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def video_generator(title, alpha):
    stream = VideoGear(source=f"media/{title}").start()
    frame_rate = 60
    while True:
        frame = stream.read()
        if frame is None:
            break
        frame_shape = frame.shape
        frame_width = frame_shape[1]
        frame_height = frame_shape[0]

        random_filename = str(uuid.uuid4()) + ".mp4"
        writer = cv2.VideoWriter(
            f"media/{random_filename}",
            cv2.VideoWriter_fourcc(*'mp4v'),
            30,
            (frame_width, frame_height)
        )
        for _ in range(frame_rate * 2):
            writer.write(frame)
            frame = stream.read()
        writer.release()
        output = str(uuid.uuid4()) + ".mp4"

        ffmpeg_str = f"ffmpeg -i media/{random_filename} -c:v libx264 -crf 20 -c:a copy media/{output}"
        if alpha:
            ffmpeg_str = f"ffmpeg -i media/{random_filename} -vf eq=contrast={alpha} -c:v libx264 -crf 20 -c:a copy media/{output}"

        subprocess.run(ffmpeg_str.split())
        subprocess.run(f"rm media/{random_filename}".split())
        yield output


@app.get('/video_part/{video_filename}/')
async def get_video_filename(request: Request, video_filename: str):
    video_filename = f"media/{video_filename}"
    return FileResponse(video_filename, media_type="video/mp4")


@app.get('/start_streaming/{title}/')
async def video_feed(title: str, response: Response, alpha: typing.Optional[float] = None):
    session_id = str(uuid.uuid4())
    start_frame_id = session_id + "_start_frame"
    framechunks_generator = video_generator(title, alpha)
    start_framechunk_filename = next(framechunks_generator)

    queue[start_frame_id] = {
        "generator": framechunks_generator,
        "next_frame_id": None,
    }

    response.set_cookie(key="session_id", value=start_frame_id)
    return {'start_filename': start_framechunk_filename}


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=5000, access_log=False)
