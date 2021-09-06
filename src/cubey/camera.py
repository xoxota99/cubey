"""
    Camera control module, including functions for scanning and
    returning best-guess color state of the camera-facing cube "edge".
"""
from cv2 import cv2     # OpenCV 4.5.3 and later
import numpy as np
# import os.path
import time

import yaml
import logging

test_color_in_position_str = "Testing color {0} in position {1}:"
against_color_str = "     against '{0}', ({1}), distance is {2}."
i_guess_color_str = "I guess color {0} is {1} , with distance {2}"


def guess_color_normalized_euclidean(raw_color, idx, calib_data):
    """Guess color using Normalized Euclidean distance"""
    norm_v = [float(i) / max(raw_color) for i in raw_color]
    best_dist = 0
    best_color = None
    logging.info(test_color_in_position_str.format(raw_color, idx))
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
        logging.info(i_guess_color_str.format(
            raw_color, best_color, best_dist))
        return best_color
    else:
        return 'X'  # Unknown color.


def guess_color_euclidean(raw_color, idx, calib_data):
    """Guess color using Euclidean distance"""
    best_dist = 0
    best_color = None
    logging.info(test_color_in_position_str.format(raw_color, idx))
    for _, (k, v2) in enumerate(calib_data["colors"]):
        rgb = v2['rgb'][idx]
        dist2 = (rgb[0] - raw_color[0]) ** 2 + \
            (rgb[1] - raw_color[1]) ** 2 + \
            (rgb[2] - raw_color[2]) ** 2

        logging.info(against_color_str.format(
            k, rgb, dist2))
        if dist2 < best_dist or best_color is None:
            best_dist = dist2
            best_color = k

    if best_color >= 0:  # and best_dist < colorCenters[best_color]['radius']:
        logging.info(i_guess_color_str.format(
            raw_color, best_color, best_dist))
        return best_color
    else:
        return 'X'  # Unknown color.


def guess_color_cie2000(raw_color, idx, calib_data):
    """
    Guess the color using the CIE2000 color space transformation, per http://hanzratech.in/2015/01/16/color-difference-between-2-colors-using-python.html
    """
    from colormath.color_objects import sRGBColor, LabColor
    from colormath.color_conversions import convert_color
    from colormath.color_diff import delta_e_cie2000

    color1_rgb = sRGBColor(raw_color[2], raw_color[1], raw_color[0])
    best_dist = 0
    best_color = None
    logging.info(test_color_in_position_str.format(raw_color, idx))
    for _, (k, v2) in enumerate(calib_data["colors"]):
        rgb = v2['rgb'][idx]
        color2_rgb = sRGBColor(rgb[2], rgb[1], rgb[0])
        color1_lab = convert_color(color1_rgb, LabColor)
        color2_lab = convert_color(color2_rgb, LabColor)
        # Find the color difference using CIE2000
        dist = delta_e_cie2000(color1_lab, color2_lab)
        logging.info(against_color_str.format(
            k, rgb, dist))
        if dist < best_dist or best_color is None:
            best_dist = dist
            best_color = k

    if best_color >= 0:  # and best_dist < colorCenters[best_color]['radius']:
        logging.info(i_guess_color_str.format(
            raw_color, best_color, best_dist))
        return best_color
    else:
        return 'X'  # Unknown color.


def guess_color_linalg(raw_color, idx, calib_data):
    """
    Guess the color using numpy's crappy linalg normalization.
        raw_color - the raw color data (from the camera)
        idx - the index facelet to test
        calib_data - calibrated data for a specific color
    """

    best_dist = 0
    best_color = None  # one of "W","O","R","B","G","Y"
    logging.info(test_color_in_position_str.format(raw_color, idx))
    for _, (color_name, calib_color_data) in enumerate(calib_data["colors"]):
        # the calibrated RGB data for this color, in this position.
        rgb = calib_color_data['rgb'][idx]
        # get the "distance" to this candidate color.
        dist = np.linalg.norm(raw_color - rgb)

        logging.info(against_color_str.format(
            color_name, rgb, dist))
        if dist < best_dist or best_color == -1:
            best_dist = dist    # how "close" are we to the idealized calibrated color?
            # best color so far. color_name is one of "W","O","R","B","G","Y"
            best_color = color_name

    if best_color >= 0:  # and best_dist < colorCenters[best_color]['radius']:
        logging.info(i_guess_color_str.format(
            raw_color, best_color, best_dist))
        return best_color
    else:
        return 'X'  # Unknown color.


# function pointer to whatever color guessing algorithm we would like to use.
guess_color = guess_color_linalg


# def devIdFromPath(path):
#     realpath = os.path.realpath(path)
#     if not "/dev/video" in realpath:
#         raise "Not a video device"
#     devnum = int(realpath[-1])
#     return devnum


class Camera:
    vidcap = None

    sample_coords = []

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
        self.sample_coords = config['cam']['colorSampleCoords']

        # self.warmup_time(cfg['cam']['warmup_delay_ms'])
        self.warmup_frames(30)

    def get_raw_colors(self, filename=None):
        """
        Given a camera reference, take a vertical edge-on picture of the cube, and 
        return an array of raw RGB values that refer to the facelets in the (zero-based) 
        F2, R0, F5, R3, F8, R6 positions., one for each of the coordinates in 
        config.colorSampleCoords.
        """
        arr = []

        # take a couple of frames. For a USB camera, frames can be buffered on the device,
        # so it can take time between the actual scene changing, and an updated frame popping
        # out of the buffer.

        self.warmup_frames(4)
        _, frame = self.vidcap.read()   # take a picture.

        if frame is not None:

            if self.config['cam']['flipCamera']:
                logging.info("FLIP")
                frame = cv2.flip(
                    frame, flipCode=self.config['cam']['flipCode'])

            # frame = (frame/256).astype('uint8')         # convert to 8-bit.
            is_black = True
            r = self.calib_data["sample_size"]
            for coord in self.sample_coords:    # for each of the edge facelet coords
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

    def get_faces(self):
        """
            Given a set of colors, return an array of FURBDL values 
            So, rather than returning e.g. "W" (for White), return "D" (for Down)
        """
        arr = self.get_raw_colors()
        retval = []
        for idx, raw_color in enumerate(arr):
            # Given the raw color, guess the actual color, based on calibrated lightning conditions.
            adj_color = guess_color(raw_color, idx, self.calib_data["colors"])
            face = self.config['cam']['colorFaceMap'][adj_color]

            retval.append(face)

# TODO: wtf is this.
            return tuple(retval)
        else:
            logging.warn("no frames!")
            return tuple(np.full(6, "X"))
# /TODO


if __name__ == "__main__":
    config_file = "../config.yaml"
    config = {}
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    calib_file = "../"+config['cam']['calibration']
    calib = {}
    with open(calib_file, 'r') as ymlfile:
        calib = yaml.load(ymlfile)

    camera = Camera(config, calib)

    # camera = Camera(cfg['cam']['camera_deviceName'],
    #                 colorSampleCoords["front"], calib["calib"]["colors"])

    logging.info(camera.get_faces())
