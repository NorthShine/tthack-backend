from fastapi import FastAPI
from fastapi.responses import Response
from starlette.requests import Request

app = FastAPI()


@app.post("/video/")
def stream_video(request: Request):
    body = b''
    async for chunk in request.stream():
        body += chunk
    response = Response(body, media_type='video/mp4')
    return response
