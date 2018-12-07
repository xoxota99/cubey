"""
    Camera control module, including functions for scanning and
    returning best-guess color state of the camera-facing cube "edge".
"""
import cv2
import numpy as np
import os.path
import time
# from config import cfg

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import yaml
import logging

# logging.basicConfig(
#     level=logging.getLevelName(cfg['app']['logLevel']), format=cfg['app']['logFormat'])


# Map Color codes (OWYBGR) to Face codes (FBTLRB).
# we take this extra step here, instead of inline in COLOR_CENTERS, to allow for configuring
# the "known" position of cube faces at startup. Because we can't scan the center facelet
# of each side (it is obscured by the gripper), we have to assume that it's a certain color for each side.
# this is basically a config value that describes the positioning of the cube in the robot.
# COLOR_TO_FACE = cfg['cam']['colorFaceMap']

# FRAME_WIDTH = cfg['cam']['frameWidth']
# FRAME_HEIGHT = cfg['cam']['frameHeight']
# FPS = cfg['cam']['fps']

# # Should we flip the camera image? (Some webcams mirror by default. Super annoying.)
# FLIP_CAMERA = cfg['cam']['flipCamera']
# FLIP_CODE = cfg['cam']['flipCode']


def guessColor_normalized_euclidean(v, idx, calib_data):
    """Guess color using Euclidean distance"""
    norm_v = [float(i) / max(v) for i in v]
    best_dist = 0
    best_color = None
    logging.info("Testing color {0} in position {1}:".format(v, idx))
    for _, (k, v2) in enumerate(calib_data["colors"]):
        rgb = v2['rgb'][idx]
        norm_rgb = [float(i) / max(rgb) for i in rgb]

        dist2 = (norm_rgb[0] - norm_v[0]) ** 2 + \
            (norm_rgb[1] - norm_v[1]) ** 2 + \
            (norm_rgb[2] - norm_v[2]) ** 2

        logging.info("     against '{0}', ({1}), normalized distance is {2}.".format(
            k, rgb, dist2))
        if dist2 < best_dist or best_color is None:
            best_dist = dist2
            best_color = k

    if best_color >= 0:  # and best_dist < colorCenters[best_color]['radius']:
        logging.info("I guess color {0} is '{1}' , with distance {2}".format(
            v, best_color, best_dist))
        return best_color
    else:
        return 'X'


def guessColor_euclidean(v, idx, calib_data):
    """Guess color using Euclidean distance"""
    best_dist = 0
    best_color = None
    logging.info("Testing color {0} in position {1}:".format(v, idx))
    for _, (k, v2) in enumerate(calib_data["colors"]):
        rgb = v2['rgb'][idx]
        dist2 = (rgb[0] - v[0]) ** 2 + \
            (rgb[1] - v[1]) ** 2 + \
            (rgb[2] - v[2]) ** 2

        logging.info("     against '{0}', ({1}), distance is {2}.".format(
            k, rgb, dist2))
        if dist2 < best_dist or best_color is None:
            best_dist = dist2
            best_color = k

    if best_color >= 0:  # and best_dist < colorCenters[best_color]['radius']:
        logging.info("I guess color {0} is {1} , with distance {2}".format(
            v, best_color, best_dist))
        return best_color
    else:
        return 'X'


def guessColor_cie2000(v, idx, calib_data):
    """
    Guess the color using the CIE2000 color space transformation, per http://hanzratech.in/2015/01/16/color-difference-between-2-colors-using-python.html
    """
    color1_rgb = sRGBColor(v[2], v[1], v[0])
    best_dist = 0
    best_color = None
    logging.info("Testing color {0} in position {1}:".format(v, idx))
    for _, (k, v2) in enumerate(calib_data["colors"]):
        rgb = v2['rgb'][idx]
        color2_rgb = sRGBColor(rgb[2], rgb[1], rgb[0])
        color1_lab = convert_color(color1_rgb, LabColor)
        color2_lab = convert_color(color2_rgb, LabColor)
        # Find the color difference using CIE2000
        dist = delta_e_cie2000(color1_lab, color2_lab)
        logging.info("     against '{0}', ({1}), distance is {2}.".format(
            k, rgb, dist))
        if dist < best_dist or best_color is None:
            best_dist = dist
            best_color = k

    if best_color >= 0:  # and best_dist < colorCenters[best_color]['radius']:
        logging.info("I guess color {0} is {1} , with distance {2}".format(
            v, best_color, best_dist))
        return best_color
    else:
        return 'X'


def guessColor_linalg(v, idx, calib_data):
    """
    Guess the color using numpy's crappy linalg normalization.
    """

    best_dist = 0
    best_color = None
    logging.info("Testing color {0} in position {1}:".format(v, idx))
    for _, (k, v2) in enumerate(calib_data["colors"]):
        rgb = v2['rgb'][idx]
        dist = np.linalg.norm(v - rgb)

        logging.info("     against '{0}', ({1}), distance is {2}.".format(
            k, rgb, dist))
        if dist < best_dist or best_color == -1:
            best_dist = dist
            best_color = k

    if best_color >= 0:  # and best_dist < colorCenters[best_color]['radius']:
        logging.info("I guess color {0} is {1} , with distance {2}".format(
            v, best_color, best_dist))
        return best_color
    else:
        return 'X'


# function pointer to whatever color guessing algorithm we would like to use.
guessColor = guessColor_linalg


# def devIdFromPath(path):
#     realpath = os.path.realpath(path)
#     if not "/dev/video" in realpath:
#         raise "Not a video device"
#     devnum = int(realpath[-1])
#     return devnum


class Camera:
    vidcap = None

    sampleCoords = []

    def get_settings(self):
        return {
            "brightness": self.vidcap.get(cv2.CAP_PROP_BRIGHTNESS),
            "contrast": self.vidcap.get(cv2.CAP_PROP_CONTRAST),
            "saturation": self.vidcap.get(cv2.CAP_PROP_SATURATION),
            "hue": self.vidcap.get(cv2.CAP_PROP_HUE),
            "gain": self.vidcap.get(cv2.CAP_PROP_GAIN),
            "auto_exposure": self.vidcap.get(cv2.CAP_PROP_AUTO_EXPOSURE),
            "exposure": self.vidcap.get(cv2.CAP_PROP_EXPOSURE),
            "sample_size": self.calib_data["sample_size"]
        }

    def warmup_time(self, millis):
        t = time.time() * 1000
        while True:
            s = time.time() * 1000
            if s - t <= millis:
                self.vidcap.grab()
            else:
                break

    def warmup_frames(self, frames):
        for _ in range(frames):
            self.vidcap.grab()

    def __init__(self, config, calib_data):
        # logging.info("resolving device for path '{0}'".format(deviceName))
        # dev_id = devIdFromPath(deviceName)
        # logging.info("path '{0}' resolved to device ID {1}".format(
        #     deviceName, dev_id))
        self.config = config
        self.vidcap = cv2.VideoCapture(config['cam']['camera_deviceID'])

        self.vidcap.set(cv2.CAP_PROP_FRAME_WIDTH, config['cam']['frameWidth'])
        self.vidcap.set(cv2.CAP_PROP_FRAME_HEIGHT,
                        config['cam']['frameHeight'])
        self.vidcap.set(cv2.CAP_PROP_FPS, config['cam']['fps'])

        if calib_data["camera"]["brightness"] != "default":
            self.vidcap.set(cv2.CAP_PROP_BRIGHTNESS,
                            calib_data["camera"]["brightness"])
        if calib_data["camera"]["contrast"] != "default":
            self.vidcap.set(cv2.CAP_PROP_CONTRAST,
                            calib_data["camera"]["contrast"])
        if calib_data["camera"]["saturation"] != "default":
            self.vidcap.set(cv2.CAP_PROP_SATURATION,
                            calib_data["camera"]["saturation"])
        if calib_data["camera"]["hue"] != "default":
            self.vidcap.set(cv2.CAP_PROP_HUE, calib_data["camera"]["hue"])
        if calib_data["camera"]["gain"] != "default":
            self.vidcap.set(cv2.CAP_PROP_GAIN, calib_data["camera"]["gain"])
        if calib_data["camera"]["auto_exposure"] != "default":
            self.vidcap.set(cv2.CAP_PROP_AUTO_EXPOSURE,
                            calib_data["camera"]["auto_exposure"])
        if calib_data["camera"]["exposure"] != "default":
            self.vidcap.set(cv2.CAP_PROP_EXPOSURE,
                            calib_data["camera"]["exposure"])

        self.calib_data = calib_data
        self.sampleCoords = config['cam']['colorSampleCoords']

        # self.warmup_time(cfg['cam']['warmup_delay_ms'])
        self.warmup_frames(30)

    def get_raw_colors(self, filename=None):
        arr = []

        self.warmup_frames(4)

        _, frame = self.vidcap.read()
        if frame is not None:

            if self.config['cam']['flipCamera']:
                logging.info("FLIP")
                frame = cv2.flip(
                    frame, flipCode=self.config['cam']['flipCode'])

            # frame = (frame/256).astype('uint8')         # convert to 8-bit.
            is_black = True
            r = self.calib_data["sample_size"]
            for coord in self.sampleCoords:
                x, y = coord[0], coord[1]

                # define a small square (x1,y1,x2,y2) in the frame to sample for color.
                x1, y1 = x - r, y - r
                x2, y2 = x + r, y + r

                block = frame[y1:y2, x1:x2]
                block_r = block[:, :, 0]    # red
                block_g = block[:, :, 1]    # green
                block_b = block[:, :, 2]    # blue

                # get the average color within the block, for each R/G/B component.
                clr = np.array(
                    (np.median(block_r), np.median(block_g), np.median(block_b))).tolist()
                # clr /= np.linalg.norm( clr ) / 255.0
                if is_black and (clr[0] != 0 or clr[1] != 0 or clr[2] != 0):
                    is_black = False

                arr.append(clr)
                if filename is not None:
                    cv2.imwrite(filename + ".png", frame)

            if is_black:
                logging.warn("All colors are BLACK. Is the lense cap on?")

            return arr
        else:
            logging.warn("no frames!")
            return np.full(6, [0.0, 0.0, 0.0]).tolist()

    def get_colors(self):
        """
            Given a camera reference, take a vertical edge-on picture of the cube, and return a tuple of FURBDL
            values that refer to the facelets in the (zero-based) F2, R0, F5, R3, F8, R6 positions.
        """
        arr = self.get_raw_colors()
        retval = []
        for idx, clr in enumerate(arr):
            code = guessColor(clr, idx, self.calib_data["colors"])
            code = self.config['cam']['colorFaceMap'][code]

            retval.append(code)

            return tuple(retval)
        else:
            logging.warn("no frames!")
            return tuple(np.full(6, "X"))


if __name__ == "__main__":
    config_file = "config.yaml"
    config = {}
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    calib_file = config['cam']['calibration']
    calib = {}
    with open(calib_file, 'r') as ymlfile:
        calib = yaml.load(ymlfile)

    camera = Camera(config, calib)

    # camera = Camera(cfg['cam']['camera_deviceName'],
    #                 colorSampleCoords["front"], calib["calib"]["colors"])

    logging.info(camera.get_colors())
