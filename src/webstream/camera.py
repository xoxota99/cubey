import numpy as np
import time
from cv2 import cv2
from frameEvent import FrameEvent
import threading
import yaml

cfg = {}
with open("../config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

calib = {}
calib_file = "../"+cfg['cam']['calibration']
with open(calib_file, 'r') as ymlfile:
    calib = yaml.load(ymlfile)

"""
Camera singleton, that publishes "frame-ready" events to any listeners.
"""

default_sample_coords = cfg["cam"]["colorSampleCoords"]
sample_size = calib["sample_size"]


class Camera(object):

    thread = None  # background thread that reads frames from camera.

    def __init__(self, source):
        """Start the background camera thread if it isn't running yet."""
        self.source = source
        self.event = FrameEvent()

        # Thread method isAlive() was renamed to is_alive() in python verson 3.9
        if Camera.thread is None or not Camera.thread.is_alive():
            self.last_access = time.time()

            # start background frame thread
            print('Starting camera thread.')
            Camera.thread = threading.Thread(
                target=self._thread)
            Camera.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0.01)

    def get_frame(self):
        """Return the current camera frame."""
        self.last_access = time.time()

        # wait for a signal from the camera thread
        self.event.wait()
        self.event.clear()

        return self.frame

    def _thread(self):
        """Camera background thread."""
        frames_iterator = self.frames()
        for frame in frames_iterator:
            self.frame = frame
            self.event.set()  # send signal to clients
            time.sleep(0.01)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            if time.time() - self.last_access > 10:
                frames_iterator.close()
                print('Stopping camera thread due to inactivity.')
                break
        Camera.thread = None

    def frames(self):

        cap = cv2.VideoCapture(self.source)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # CV_CAP_PROP_FRAME_WIDTH
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # CV_CAP_PROP_FRAME_HEIGHT
        cap.set(cv2.CAP_PROP_FPS, 60)   # CAP_PROP_FPS

        # warmup the cameras. Discard all frames for two seconds.
        t = time.time() * 1000

        while True:
            s = time.time() * 1000
            if s - t <= 2000:
                cap.grab()
            else:
                break

        while True:
            # read current frame
            _, frame = cap.read()

            # overlay sampling coordinates.
            num = 1
            for coord in default_sample_coords:
                cv2.rectangle(
                    frame, (coord[0] - sample_size, coord[1] - sample_size), (coord[0] + sample_size, coord[1] + sample_size), (0, 255, 0), 2)
                cv2.putText(
                    frame, str(num), (coord[0] + sample_size, coord[1] - sample_size), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                cv2.line(frame, (320, 0), (320, 30), (0.0, 255.0, 0.0), 2)
                cv2.line(frame, (320, 480), (320, 450), (0.0, 255.0, 0.0), 2)
                cv2.line(frame, (0, 240), (30, 240), (0.0, 255.0, 0.0), 2)
                cv2.line(frame, (640, 240), (610, 240), (0.0, 255.0, 0.0), 2)

                num += 1

            yield cv2.imencode('.jpg', frame)[1].tobytes()
