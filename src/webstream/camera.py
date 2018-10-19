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

    thread = None  # background thread that reads frames from camera.
    # frame = None  # current frame is stored here by background thread
    # last_access = 0  # time of last client access to the camera
    # event = FrameEvent()

    def __init__(self, source_front_right, source_back_left):
        """Start the background camera thread if it isn't running yet."""
        self.source_front_right = source_front_right
        self.source_back_left = source_back_left
        self.event = FrameEvent()

        if Camera.thread is None or not Camera.thread.isAlive():
            self.last_access = time.time()

            # start background frame thread
            print('Starting camera thread.')
            Camera.thread = threading.Thread(
                target=self._thread)
            Camera.thread.start()

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
        Camera.thread = None

    def frames(self):

        cap_fr = cv2.VideoCapture(self.source_front_right)
        cap_fr.set(3, 640)  # CV_CAP_PROP_FRAME_WIDTH
        cap_fr.set(4, 480)  # CV_CAP_PROP_FRAME_HEIGHT
        cap_fr.set(5, 15)   # CAP_PROP_FPS

        cap_bl = cv2.VideoCapture(self.source_back_left)
        cap_bl.set(3, 640)  # CV_CAP_PROP_FRAME_WIDTH
        cap_bl.set(4, 480)  # CV_CAP_PROP_FRAME_HEIGHT
        cap_bl.set(5, 15)   # CAP_PROP_FPS

        while True:
            # read current frame
            _, frame_fr = cap_fr.read()
            _, frame_bl = cap_bl.read()

            # TODO: Overlay text "Front/Right" and "Back/Left" over relevant feeds.
            # TODO: Overlay sampling coordinates
            vis = np.concatenate((frame_fr, frame_bl), axis=1)

            yield cv2.imencode('.jpg', vis)[1].tobytes()
