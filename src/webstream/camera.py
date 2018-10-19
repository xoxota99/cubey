from __future__ import division
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
from frameEvent import FrameEvent
from datetime import datetime
import threading

"""
Camera singleton, that publishes "frame-ready" events to any listeners.
"""


class Camera(object):

    threads = {}  # background thread that reads frames from camera.
    # frame = None  # current frame is stored here by background thread
    # last_access = 0  # time of last client access to the camera
    # event = FrameEvent()

    def __init__(self, video_source):
        """Start the background camera thread if it isn't running yet."""
        self.video_source = video_source
        self.event = FrameEvent()

        if video_source not in Camera.threads or Camera.threads[video_source] is None or not Camera.threads[video_source].isAlive():
            self.last_access = time.time()

            # start background frame thread
            print('Starting camera thread.')
            Camera.threads[video_source] = threading.Thread(
                target=self._thread)
            Camera.threads[video_source].start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

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
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            if time.time() - self.last_access > 10:
                frames_iterator.close()
                print('Stopping camera thread due to inactivity.')
                break
        Camera.threads[self.video_source] = None

    def frames(self):

        vs = cv2.VideoCapture(self.video_source)
        vs.set(3, 640)  # CV_CAP_PROP_FRAME_WIDTH
        vs.set(4, 480)  # CV_CAP_PROP_FRAME_HEIGHT
        vs.set(5, 15)   # CAP_PROP_FPS

        while True:
            # read current frame
            _, frame = vs.read()
            yield cv2.imencode('.jpg', frame)[1].tobytes()
