import cv2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class VideoCamera(object):
    def __init__(self, title, alpha, beta):
        self.video = cv2.VideoCapture(f"media/{title}")
        self.video.set(3, 1280)  # float `width`
        self.video.set(4, 720)  # float `height`
        self.alpha = alpha
        self.beta = beta

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        try:
            print(image.shape)
        except:
            return

        args = {}
        if self.alpha:
            args["alpha"] = self.alpha
        if self.beta:
            args["beta"] = self.beta

        image = cv2.convertScaleAbs(image, **args)
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()


def gen(camera):
    while True:
        frame = camera.get_frame()
        if not frame:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.get('/stream/{title}')
def video_feed(title: str, alpha: float = 1, beta: float = 1):
    return StreamingResponse(gen(VideoCamera(
        title,
        alpha,
        beta,
    )), media_type="multipart/x-mixed-replace;boundary=frame")
