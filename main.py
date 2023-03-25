import base64
import typing
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, Header
from fastapi.responses import Response
from fastapi.requests import Request

from contrast import edit_contrast

app = FastAPI(debug=True)


@app.get("/stream/{title}")
async def stream_video(
        request: Request,
        title: str,
        range: str = Header(None),
        contrast: typing.Optional[int | float] = None,
):
    body = b''
    path = Path(f"media/{title}")
    with open(path, "rb") as video:
        start, end = range.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else start + 2048
        video.seek(1)
        data = video.read(end - start)
        filesize = str(path.stat().st_size)
        headers = {
            'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
            'Accept-Ranges': 'bytes',
        }

        """
        for chunk in data:
            if contrast:
                frame = np.asarray(bytearray(chunk), np.uint8)
                frame = cv2.imdecode(frame, -1)
                frame = edit_contrast(frame, contrast)
                frame = cv2.imencode('.jpg', frame)[1]
                chunk = base64.b64encode(frame).decode('utf-8')
            body += chunk
        """

    # response = Response(body, media_type="text/plain", headers=headers)
        response = Response(data, media_type="text/plain", headers=headers)
        return response
