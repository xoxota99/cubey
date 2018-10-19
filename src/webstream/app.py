#!/usr/bin/env python
from flask import Flask, render_template, Response
import argparse
from camera import Camera

app = Flask(__name__)


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
    return Response(gen(Camera(0, 1)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# TODO: Also provide a graphic of the cube's state estimation.
# TODO: Also provide controls for scrambling, scanning and solving.


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
