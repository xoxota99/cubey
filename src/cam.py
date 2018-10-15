
import cv2
import numpy as np
import os.path


def devIdFromPath(path):
    realpath = os.path.realpath(path)
    if not "/dev/video" in realpath:
        raise "Not a video device"
    devnum = int(realpath[-1])
    return devnum


class Camera:
    vidcap = None

    def __init__(self, deviceName):
            vidcap = cv2.VideoCapture(devIdFromPath(deviceName))
            vidcap.set(3, 160)   # cv2.cv.CV_CAP_PROP_FRAME_WIDTH
            vidcap.set(4, 120)   # cv2.cv.CV_CAP_PROP_FRAME_HEIGHT
