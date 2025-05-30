from flask import Flask, render_template, Response
from camera import Camera
import signal
import sys

app = Flask(__name__)
cam = None


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    if(cam != None):
        cam.stop()
    sys.exit(0)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


@app.route('/front')
def front():
    """Video streaming home page."""
    return render_template('front.html')


@app.route('/back')
def back():
    """Video streaming home page."""
    return render_template('back.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame if frame is not None else b'' + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    global cam
    cam = Camera(0)
    return Response(gen(cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# TODO: Also provide a graphic of the cube's state estimation.
# TODO: Also provide controls for scrambling, scanning and solving.


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    # signal.pause()
    print("starting")
    app.run(host='0.0.0.0', threaded=True)
