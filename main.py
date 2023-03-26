import time
import typing
import uuid

import cv2
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from vidgear.gears import CamGear, StreamGear, VideoGear, WriteGear

app = FastAPI()


@app.get('/stream/{title}')
def video_feed(title: str, alpha: float = 1):
    frame_rate = 60
    video_size = (1920, 1080)

    stream = VideoGear(source="media/1.mp4").start()
    writer = WriteGear(f"{uuid.uuid4()}.mp4", compression_mode=False)

    def video_generator():
        while True:
            frame = stream.read()
            if frame is None:
                break
            for _ in range(frame_rate * 2):
                writer.write(frame)
            writer.write(frame)
            yield

    # def frame_generator():
    #     while True:
    #         frame = stream.read()
    #         if frame is None:
    #             break
    #         ret, jpeg = cv2.imencode('.jpg', frame)
    #         jpeg = jpeg.tobytes()
    #         # yield the frame as an HTTP response so it can be sent over the web
    #         yield (b'--frame\r\n'
    #                b'Content-Type: video/mp4\r\n\r\n' + jpeg + b'\r\n')

    # define the headers for the HTTP response
    headers = {
        'Content-Type': 'multipart/x-mixed-replace; boundary=frame'
    }

    # return a StreamingResponse object with the frame generator function and headers
    return StreamingResponse(frame_generator(), headers=headers)

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=5000, access_log=False)
