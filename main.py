import typing

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
            edit_contrast(chunk, contrast)
        body += chunk

    response = Response(body, media_type="video/mp4")
    return response
