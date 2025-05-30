import logging
from cv2 import cv2     # OpenCV 4.5.3 and later
import numpy as np
import time
import math
import yaml
from time import sleep
import os
from typing import Dict, List, Tuple, Optional, Union, Any, cast
from lib.logger import setup_logging

"""
    Camera control module, including functions for scanning and
    returning best-guess color state of the camera-facing cube "edge".
"""

# Type aliases
HSVValue = np.ndarray  # Shape (3,) for H, S, V values
ColorCalibration = Dict[str, Dict[str, np.ndarray]]  # Color calibration data

test_color_in_position_str = "Testing color {0} in position {1}:"
against_color_str = "     against '{0}', ({1}), distance is {2}."
i_guess_color_str = "I guess color {0} is {1} , with distance {2}"


def test_color(raw_hsv: HSVValue, min_hsv: HSVValue, max_hsv: HSVValue) -> bool:
    """
    Return whether a given raw_hsv value is within the range of min_hsv and max_hsv.
    
    Args:
        raw_hsv: HSV value to test
        min_hsv: Minimum HSV values
        max_hsv: Maximum HSV values
        
    Returns:
        True if the raw_hsv is within the range, False otherwise
    """
    retval = True

    if max_hsv[0] < min_hsv[0]:  # special case (red)
        retval = int(raw_hsv[0]) in range(int(max_hsv[0]), int(min_hsv[0]) + 256)  # for H
    else:
        retval = int(raw_hsv[0]) in range(int(min_hsv[0]), int(max_hsv[0]) + 1)    # for H

    for i in range(1, 3):  # for each of S, V
        retval = retval and int(raw_hsv[i]) in range(int(min_hsv[i]), int(max_hsv[i]) + 1)

    return retval


def guess_color(raw_hsv: HSVValue, colors: ColorCalibration) -> str:
    """
    Given a raw hsv value, and a set of color brackets, guess what color we're looking at.
    
    Args:
        raw_hsv: HSV value to test
        colors: Dictionary of color calibration data
        
    Returns:
        Color name (one of "U","R","F","D","L","B") or "X" for unknown
    """
    best_dist = 0
    best_color = "X"  # one of "U","R","F","D","L","B". "X" is "unknown".

    for color_name in colors:
        min_hsv = np.array(colors[color_name]["min"])
        max_hsv = np.array(colors[color_name]["max"])

        if max_hsv[0] < min_hsv[0]:
            min_hsv[0] -= 255  # make minH negative.

        mid_hsv = np.mean(np.array([min_hsv, max_hsv]), axis=0)
        if test_color(raw_hsv, min_hsv, max_hsv):
            # calculate the distance between the raw HSV value and the "middle" of the range of HSV values for this color.
            dist = math.sqrt(((raw_hsv[0] - mid_hsv[0]) ** 2) + (
                (raw_hsv[1] - mid_hsv[1]) ** 2) + ((raw_hsv[2] - mid_hsv[2]) ** 2))

            if max_hsv[0] < min_hsv[0] and raw_hsv[0] > min_hsv[0] + 255:
                # special case, when color is red. mid_hsv can end up on the opposite end of
                # the H spectrum from raw_hsv, producing an incorrect distance.
                dist = math.sqrt(((raw_hsv[0] - 255 - mid_hsv[0]) ** 2) + (
                    (raw_hsv[1] - mid_hsv[1]) ** 2) + ((raw_hsv[2] - mid_hsv[2]) ** 2))
            elif max_hsv[0] < min_hsv[0] and raw_hsv[0] < max_hsv[0]:
                # Another edge case for red when raw_hsv is on the low end of the spectrum
                dist = math.sqrt(((raw_hsv[0] + 255 - mid_hsv[0]) ** 2) + (
                    (raw_hsv[1] - mid_hsv[1]) ** 2) + ((raw_hsv[2] - mid_hsv[2]) ** 2))

            if best_dist == 0 or dist < best_dist:
                best_color = color_name
                best_dist = dist

    if best_color == "X":
        logging.warning("UNKNOWN COLOR {0}".format(raw_hsv))
    else:
        logging.info(i_guess_color_str.format(raw_hsv, best_color, best_dist))
    def get_settings(self) -> Dict[str, Any]:
        """
        Get current camera settings
        
        Returns:
            dict: Dictionary of camera settings
        """
        return {
            "CAP_PROP_BRIGHTNESS": self.vidcap.get(cv2.CAP_PROP_BRIGHTNESS),
            "CAP_PROP_CONTRAST": self.vidcap.get(cv2.CAP_PROP_CONTRAST),
            "CAP_PROP_SATURATION": self.vidcap.get(cv2.CAP_PROP_SATURATION),
            "CAP_PROP_HUE": self.vidcap.get(cv2.CAP_PROP_HUE),
            "CAP_PROP_GAIN": self.vidcap.get(cv2.CAP_PROP_GAIN),
            "CAP_PROP_AUTO_EXPOSURE": self.vidcap.get(cv2.CAP_PROP_AUTO_EXPOSURE),
            "CAP_PROP_EXPOSURE": self.vidcap.get(cv2.CAP_PROP_EXPOSURE),
            "sample_aperture": self.config["cam"]["sample_aperture"]
        }

    def warmup_frames(self, frames: int) -> None:
        """
        Grab a specified number of frames to clear the camera buffer
        
        Args:
            frames: Number of frames to grab
        """
        success_count = 0
        max_attempts = frames * 2  # Allow for some failures
        attempts = 0
        
        while success_count < frames and attempts < max_attempts:
            if self.vidcap.grab():
                success_count += 1
            attempts += 1
            
        if success_count < frames:
            logging.warning(f"Could only grab {success_count}/{frames} frames during warmup")
            
        # Small delay to ensure frames are processed
        sleep(0.05)
    return best_color


class Camera:
    """Camera class for capturing and processing cube images"""
    
    vidcap = None
    sample_coords: List[List[int]] = []
    
    def __init__(self, config: Dict[str, Any], calib_data: Dict[str, Any]) -> None:
        """
        Initialize the camera with configuration and calibration data
        
        Args:
            config: Configuration dictionary
            calib_data: Calibration data dictionary
        """
        self.config = config
        self.vidcap = cv2.VideoCapture(config["cam"]["camera_deviceID"])

        for prop_name in calib_data["camera"]:
            if calib_data["camera"][prop_name] != "default" and hasattr(cv2, prop_name):
                self.vidcap.set(getattr(cv2, prop_name),
                                calib_data["camera"][prop_name])

        self.calib_data = calib_data
        self.sample_coords = config['cam']['sample_coords']

        self.warmup_frames(config['cam']['warmup_frames'])
        
    def __del__(self) -> None:
        """Clean up camera resources when the object is destroyed"""
        if self.vidcap is not None:
            self.vidcap.release()
            
    def close(self) -> None:
        """Explicitly release camera resources"""
        if self.vidcap is not None:
            self.vidcap.release()
            self.vidcap = None

    def get_raw_hsv(self, filename: Optional[str] = None) -> List[HSVValue]:
        """
        Given a camera reference, take a vertical edge-on picture of the cube, and
        return an array of raw hsv values that refer to the facelets in the (zero-based)
        F2, R0, F5, R3, F8, R6 positions, one for each of the coordinates in
        config.sample_coords.
        
        Args:
            filename: Optional filename to save the captured image for debugging
            
        Returns:
            List of HSV values for each sampled facelet
        """
        retval: List[HSVValue] = []

        # take a couple of frames. For a USB camera, frames can be buffered on the device,
        # so it can take time between the actual scene changing, and an updated frame popping
        # out of the buffer.

        self.warmup_frames(4)
        _, frame = self.vidcap.read()   # take a picture.

        if frame is None:
            logging.warning("no frames!")
            return cast(List[HSVValue], np.full((6, 3), [0.0, 0.0, 0.0]).tolist())

        hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)

        if self.config['cam']['flip_camera']:
            logging.info("FLIP")
            hsvframe = cv2.flip(
                hsvframe, flipCode=self.config['cam']['flip_code'])

        is_black = True
        r = self.config["cam"]["sample_aperture"]
        for coord in self.sample_coords:    # for each of the 6 edge facelet coords
            x, y = coord[0], coord[1]

            # define a small square (x1,y1,x2,y2) in the frame to sample for color.
            x1, y1 = x - r, y - r
            x2, y2 = x + r, y + r

            block = hsvframe[y1:y2, x1:x2]

            # average hsv in the sample area.
            avg = block.mean(axis=0).mean(axis=0)

            # value is "too dark". (value ==0/255)
            is_black = is_black and avg[2] == 0

            retval.append(avg)   # append average hsv values.
            if filename is not None:
                # draw the sample aperture on the raw frame.
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "h: {0}\ns: {1}\nv: {2}".format(avg[0], avg[1], avg[2]), (x2, y2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if filename is not None:
            # write the captured raw image, for debugging.
            cv2.imwrite(filename + ".png", frame)

        if is_black:
            logging.warning("All colors are BLACK. Is the lense cap on?")

        return retval

    def get_faces(self, filename: Optional[str] = None) -> Tuple[str, str, str, str, str, str]:
        """
        Given an array of HSV values, return an array of FURBDL values
        
        Args:
            filename: Optional filename to save the captured image for debugging
            
        Returns:
            Tuple of 6 color values (one for each facelet)
        """
        arr = self.get_raw_hsv(filename)
        retval: List[str] = []
        for idx, raw_hsv in enumerate(arr):
            # Given the raw color, guess the actual color, based on calibrated lightning conditions.
            logging.info(test_color_in_position_str.format(raw_hsv, idx))
            adj_color = guess_color(
                raw_hsv, self.calib_data["colors"])

            retval.append(adj_color)

        # Ensure we always return exactly 6 values
        while len(retval) < 6:
            retval.append("X")  # Add unknown color if we don't have enough
            
        # Cast to the expected return type
        return cast(Tuple[str, str, str, str, str, str], tuple(retval))


if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_file = os.path.join(script_dir, "config.yaml")
    config = {}
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # Set up logging using the centralized logger
    setup_logging(config_file)
    logger = logging.getLogger(__name__)

    calib_file = os.path.join(script_dir, config['cam']['calibration'])
    calib = {}
    with open(calib_file, 'r') as ymlfile:
        calib = yaml.load(ymlfile, Loader=yaml.FullLoader)

    camera = Camera(config, calib)

    logging.info(camera.get_faces("test"))
