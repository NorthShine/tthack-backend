import time
import typing
import uuid
import os

import cv2
import uvicorn
from fastapi import FastAPI, Request
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


def parse_range_request_header(str_header: str) -> dict:
    header_content = {
        "unit": "bytes",
        "start_range": 0,
        "end_range": None
    }

    range_header: list[str] = str_header.split("=")
    if len(range_header) < 2:
        return header_content

    header_content["unit"] = range_header[0].strip()
    range_header[1] = range_header[1].strip()
    chunk_range: list[str] = range_header[1].split("-")
    if len(chunk_range) == 2:
        header_content["start_range"] = int(chunk_range[0])

        if chunk_range[1].isnumeric():
            header_content["end_range"] = int(chunk_range[1])

    return header_content


@app.get('/video_part/{video_filename}/')
async def get_video_filename(request: Request, video_filename: str):
    video_filename = f"media/{video_filename}"
    try:
        next_filename = next(generator)
    except StopIteration:
        return {"detail": "stream_finished"}

    file_stat = os.stat(video_filename)
    content_length: int = file_stat.st_size

    range_unit: str = "bytes"
    start_range: int = 0
    buffer_range: int = content_length

    def iterfile():
        nonlocal start_range, buffer_range
        with open(f"{video_filename}", "rb", 2048) as file_ref:
            file_ref.seek(start_range)
            yield file_ref.read(buffer_range)

    if "range" in request.headers:
        range_request = parse_range_request_header(request.headers["range"])

        start_range = int(range_request["start_range"])
        if start_range > content_length:
            start_range = content_length

        if range_request["end_range"] is not None:
            buffer_range = int(range_request["end_range"]) - start_range

        left_bytes: int = content_length - start_range
        if buffer_range > left_bytes:
            buffer_range = left_bytes

    headers = {
        "Next-Part": str(next_filename)
    }
    headers["Content-Range"] = f"{range_unit} {start_range}-{buffer_range + start_range}/{content_length}"
    headers["Content-Length"] = str(buffer_range)

    response_status: int = 206
    if buffer_range == 0:
        response_status = 204

    return StreamingResponse(iterfile(), response_status, media_type="video/mp4", headers=headers)


@app.get('/start_streaming/')
async def video_feed():
    current_filename = next(generator)
    return {'start_filename': current_filename}

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=5000, access_log=False)
