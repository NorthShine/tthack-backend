import base64
import typing

import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.requests import Request

from contrast import edit_contrast

app = FastAPI(debug=True)


@app.post("/video/")
def stream_video(
        request: Request,
        contrast: typing.Optional[int] = None,
):
    body = b''
    async for chunk in request.stream():
        if contrast:
            frame = np.asarray(bytearray(chunk), np.uint8)
            frame = cv2.imdecode(frame, -1)
            frame = edit_contrast(frame, contrast)
            frame = cv2.imencode('.jpg', frame)[1]
            chunk = base64.b64encode(frame).decode('utf-8')
        body += chunk

    response = Response(body, media_type="text/plain")
    return response
