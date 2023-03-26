import time
import cv2
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


class VideoCamera(object):
    def __init__(self, title):
        self.video = cv2.VideoCapture(f"media/{title}")
        self.video.set(3, 1280)  # float `width`
        self.video.set(4, 720)  # float `height`

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        try:
            print(image.shape)
        except:
            return
        image = cv2.convertScaleAbs(image, alpha=2.5)
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()


def gen(camera):
    c = 1
    start = time.time()
    while True:
        start_1 = time.time()
        if c % 20 == 0:
            end = time.time()
            FPS = 20 / (end-start)
            print("FPS_avg : {:.6f} ".format(FPS))
            start = time.time()
        frame = camera.get_frame()
        if not frame:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        end_1 = time.time()
        FPS = 1/(end_1-start_1)
        print("FPS : {:.6f} ".format(FPS))
        c += 1


@app.get('/stream/{title}')
def video_feed(title: str):
    return StreamingResponse(gen(VideoCamera(title)), media_type="multipart/x-mixed-replace;boundary=frame")


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=5000, access_log=False)
