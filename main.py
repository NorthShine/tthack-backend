import os
import base64
import typing

import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.requests import Request

from contrast import edit_contrast

app = FastAPI(debug=True)


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


@app.get("/stream/{title}")
async def stream_video(
        request: Request,
        title: str,
        contrast: typing.Optional[int | float] = None,
):
    file_path: str = f"media/{title}"
    mimetype: str = "video/mp4"
    file_stat = os.stat(file_path)
    content_length: int = file_stat.st_size

    range_unit: str = "bytes"
    start_range: int = 0
    buffer_range: int = content_length

    headers = {}

    def read_file():
        nonlocal file_path, start_range, buffer_range
        with open(file_path, "rb", 2048) as file_ref:
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

    headers["Content-Range"] = f"{range_unit} {start_range}-{buffer_range + start_range}/{content_length}"
    headers["Content-Length"] = str(buffer_range)

    response_status: int = 206
    if buffer_range == 0:
        response_status = 204

    return StreamingResponse(read_file(), response_status, headers, mimetype)

"""
for chunk in data:
    if contrast:
        frame = np.asarray(bytearray(chunk), np.uint8)
        frame = cv2.imdecode(frame, -1)
        frame = edit_contrast(frame, contrast)
        frame = cv2.imencode('.jpg', frame)[1]
        chunk = base64.b64encode(frame).decode('utf-8')
    body += str(chunk).encode("utf-8")
"""
