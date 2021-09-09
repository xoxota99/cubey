import numpy as np
import logging
import yaml
import math
import sys

from lib import camera
from lib.motorcontroller import MotorController

"""
Utility for creating HSV calibration data
"""

config_file = "config.yaml"
config = {}
with open(config_file, 'r') as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)

logging.basicConfig(
    level=logging.getLevelName(config['app']['logLevel']), format=config['app']['logFormat'])

colorSampleCoords = config['cam']['colorSampleCoords']
calib_file = config['cam']['calibration']
calib = {}
with open(calib_file, 'r') as ymlfile:
    calib = yaml.load(ymlfile, Loader=yaml.FullLoader)

camera = camera.Camera(config, calib)


def collision_detect(config):
    errors = []
    compared = {"R": [], "O": [], "Y": [], "G": [], "B": [], "W": []}
    cal = config["colors"]

    for key1 in cal:  # 6
        min_hsv_1 = cal[key1]["min"]
        max_hsv_1 = cal[key1]["max"]
        for key2 in cal:  # 5, 4, 3, 2, 1
            compared[key1].append(key2)
            if key2 != key1 and key1 not in compared[key2]:
                min_hsv_2 = cal[key2]["min"]
                max_hsv_2 = cal[key2]["max"]
                # print("#Testing {0} against {1}".format(key1, key2))
                # TODO: doesn't capture red / modulo
                if (max_hsv_1[0] > min_hsv_2[0]) and (min_hsv_1[0] < max_hsv_2[0]) and (max_hsv_1[1] > min_hsv_2[1]) and (min_hsv_1[1] < max_hsv_2[1]) and (max_hsv_1[2] > min_hsv_2[2]) and (min_hsv_1[2] < max_hsv_2[2]):
                    errors.append(
                        {
                            "color1": key1,
                            "min_hsv_1": cal[key1]["min"],
                            "max_hsv_1": cal[key1]["max"],
                            "color2": key1,
                            "min_hsv_2": cal[key2]["min"],
                            "max_hsv_2": cal[key2]["max"]
                        }
                    )

    if len(errors) > 0:
        logging.warn("-----------------------------------------------")
        logging.warn(
            "There were collisions in the HSV color calibration:")
        for err in errors:
            logging.warn("\t{0}".format(err))
        logging.warn("-----------------------------------------------")


def calibrate(motors):
    scanstr = "scanning {0}: {1}"

    """
    Scan a (currently solved) cube, and use the mean of the resulting color values as calibrated color centers for each edge / corner facelet.
    Generate min/max values based on the known values encountered.

    WE ASSUME: That the cube is fully solved, and present in a known orientation (Orange face front, Yellow face up).
    """

    # colors, in HSV format.

    colors = {
        'O': np.zeros((6, 3)).tolist(),
        'R': np.zeros((6, 3)).tolist(),
        'G': np.zeros((6, 3)).tolist(),
        'B': np.zeros((6, 3)).tolist(),
        'Y': np.zeros((6, 3)).tolist(),
        'W': np.zeros((6, 3)).tolist()
    }

    # scan front

    colors['O'][0], colors['B'][1], colors['O'][2], colors['B'][
        3], colors['O'][4], colors['B'][5] = camera.get_raw_hsv("1_OBOBOB")

    logging.debug(scanstr.format("FR", "OBOBOB"))

    motors.execute("F2")
    _, colors['G'][1], _, colors['G'][3], _, colors['G'][5] = camera.get_raw_hsv(
        "2__G_G_G")
    logging.debug(scanstr.format("FR", "_G_G_G"))

    motors.execute("F")
    _, colors['W'][1], _, colors['W'][3], _, colors['W'][5] = camera.get_raw_hsv(
        "3__W_W_W")
    logging.debug(scanstr.format("FR", "_W_W_W"))

    motors.execute("F R")  # origin, then R.
    colors['W'][0], _, colors['W'][2], _, colors['W'][4], _ = camera.get_raw_hsv(
        "4_W_W_W_")
    logging.debug(scanstr.format("FR", "W_W_W_"))

    motors.execute("R' U R'")  # origin, then U R'
    colors['Y'][0], colors['R'][1], colors['Y'][2], colors['R'][
        3], colors['Y'][4], colors['R'][5] = camera.get_raw_hsv("5__YRYRYR")
    logging.debug(scanstr.format("FR", "YRYRYR"))

    motors.execute("R U' R U F")  # origin, then R U F
    colors['B'][0], colors['O'][1], colors['B'][2], colors['O'][
        3], colors['B'][4], colors['O'][5] = camera.get_raw_hsv("6_BOBOBO")
    logging.debug(scanstr.format("FR", "BOBOBO"))

    motors.execute("F' U' R' U' F")  # origin, then U' F
    colors['G'][0], _, colors['G'][2], _, colors['G'][4], _ = camera.get_raw_hsv(
        "7_G_G_G_")
    logging.debug(scanstr.format("FR", "G_G_G_"))

    motors.execute("F' U' F")
    colors['R'][0], colors['Y'][1], colors['R'][2], colors['Y'][
        3], colors['R'][4], colors['Y'][5] = camera.get_raw_hsv("8_RYRYRY")
    logging.debug(scanstr.format("FR", "RYRYRY"))

    motors.execute("F' U2")  # back to origin

    # at this point, we've scanned all the colors on each facelet.
    # Now lets build the calibration data based on the gathered hsv raw values.
    cal = {}
    min_hsv = np.array([255, 255, 255])
    max_hsv = np.array([0, 0, 0])
    for key in colors:
        cal_entry = {}
        if(key == "R"):
            # TODO: special case.
            pass
        else:
            for hsv_entry in colors[key]:
                min_hsv = np.minimum(min_hsv, hsv_entry)
                max_hsv = np.maximum(max_hsv, hsv_entry)

        cal_entry["min"] = min_hsv
        cal_entry["max"] = max_hsv
        cal[key] = cal_entry

    # collision-detection
    collision_detect(cal)

    retval = {"colors": cal, "sample_size": camera.calib_data["sample_size"]}
    return retval


def process_args(argv):
    if len(argv) > 1:
        retval = {}
        param_name = ""
        for i, arg in enumerate(argv):
            if i % 2 == 0:
                param_name = arg
            else:
                retval[param_name] = arg
                param_name = ""
    return retval


if __name__ == "__main__":
    args = process_args(sys.argv)

    config_file = "config.yaml"
    config = {}
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    logging.basicConfig(
        level=logging.getLevelName(config['app']['logLevel']), format=config['app']['logFormat'])

    motors = MotorController(config)

    c = camera.get_settings()
    s = calibrate(motors)
    obj = {"camera": c, "calib": s}
    yaml_text = yaml.dump(obj, default_flow_style=True)

    if args["o"]:
        with open(args["o"], 'w') as outfile:
            yaml.dump(obj, outfile, default_flow_style=True)
    else:
        logging.info(yaml_text)
