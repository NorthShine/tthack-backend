import subprocess
import typing
import uuid

import cv2
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from vidgear.gears import VideoGear

from epilepthic_scene_detector.epilepthic_controller import get_epilepthic_risk

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

frames_by_title = {}


def video_generator(title, alpha):
    stream = VideoGear(source=f"media/{title}").start()
    frame_rate = 60
    risk = 0
    while True:
        frame = stream.read()
        if frame is None:
            break

        if title in frames_by_title:
            if len(frames_by_title[title]) == 5:
                risk = get_epilepthic_risk(frames_by_title[title], 30)
                frames_by_title[title] = []
            frames_by_title[title].append(frame)
        else:
            frames_by_title[title] = [frame]

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
        if risk > 0.25:
            ffmpeg_str = f"ffmpeg -i media/{random_filename} -vf eq=contrast=25 -c:v libx264 -crf 20 -c:a copy media/{output}"
        elif alpha:
            ffmpeg_str = f"ffmpeg -i media/{random_filename} -vf eq=contrast={alpha} -c:v libx264 -crf 20 -c:a copy media/{output}"

        subprocess.call(ffmpeg_str, shell=True)
        subprocess.call(f"rm media/{random_filename}", shell=True)
        yield output


@app.get('/video_part/{video_filename}/')
async def get_video_filename(request: Request, video_filename: str):
    session_id = request.cookies.get("session_id")
    generator = queue.get(session_id)
    current_frame_generator = generator["generator"] if generator is not None else None
    if current_frame_generator is None:
        return JSONResponse(
            content={"message": "End of video"},
            headers={"x-next-frame": "end"}
        )

    try:
        current_filename = next(current_frame_generator)
    except StopIteration:
        del queue[session_id]
        headers = {
            "x-next-frame": "end"
        }
        return JSONResponse(
            content={"message": "End of video"},
            headers=headers)

    headers = {
        "X-Next-Frame": current_filename,
        "media-type": "video/mp4",
        "Content-Type": "video/mp4",
    }
    video_filename = f"media/{video_filename}"
    response = FileResponse(video_filename, headers=headers, media_type="video/mp4")

    return response


@app.get('/start_streaming/{title}/')
async def video_feed(title: str, response: Response, alpha: typing.Optional[float] = None):
    session_id = str(uuid.uuid4())
    framechunks_generator = video_generator(title, alpha)
    start_framechunk_filename = next(framechunks_generator)

    queue[session_id] = {
        "generator": framechunks_generator,
    }

    response.set_cookie(key="session_id", value=session_id)
    return {'start_filename': start_framechunk_filename}


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=5000, access_log=False)
