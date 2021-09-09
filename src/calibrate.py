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
with open(config_file, "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)

logging.basicConfig(
    level=logging.getLevelName(config["app"]["logLevel"]), format=config["app"]["logFormat"])

sample_coords = config["cam"]["sample_coords"]
calib_file = config["cam"]["calibration"]
calib = {}
with open(calib_file, "r") as ymlfile:
    calib = yaml.load(ymlfile, Loader=yaml.FullLoader)

camera = camera.Camera(config, calib)


def collision_detect(config):
    collisions = []
    keys = ["F", "U", "R", "B", "L", "D"]
    cal = config["colors"]

    for i in range(0, 6):
        bracket1 = cal[keys[i]]
        for j in range(i + 1, 6):
            bracket2 = cal[keys[j]]
            collide = False

            if bracket1["max"][0] < bracket1["min"][0]:
                collide = (bracket1["max"][0] > bracket2["min"][0]) or (
                    bracket1["min"][0] < bracket2["max"][0])
            elif bracket1["max"][0] < bracket1["min"][0]:
                collide = (bracket2["max"][0] > bracket1["min"][0]) or (
                    bracket2["min"][0] < bracket1["max"][0])
            else:
                # non-red. Do these hues overlap?
                collide = (bracket1["max"][0] > bracket2["min"][0]) and (
                    bracket1["min"][0] < bracket2["max"][0])

            # now check S and V, which are the same for red and non-red.
            collide = collide and (
                bracket1["max"][1] > bracket2["min"][1]) and (
                bracket1["min"][1] < bracket2["max"][1]) and (
                bracket1["max"][2] > bracket2["min"][2]) and (
                bracket1["min"][2] < bracket2["max"][2])

            if collide:
                collisions.append(
                    {
                        keys[i]: [bracket1["min"], bracket1["max"]],
                        keys[j]: [bracket2["min"], bracket2["max"]],
                    }
                )

    if len(collisions) > 0:
        logging.warn("-----------------------------------------------")
        logging.warn("There were collisions in the HSV calibration:")
        for c in collisions:
            logging.warn("\t{0}".format(c))
        logging.warn("-----------------------------------------------")


def calibrate(motors):
    scanstr = "scanning {0}: {1}"

    """
    Scan a (currently solved) cube, and use the mean of the resulting HSV values as calibrated means for each edge / corner facelet.
    Generate min/max values based on the values encountered.

    WE ASSUME: That the cube is fully solved
    """

    # colors, in HSV format.
    facelet_hsv = {
        "F": np.zeros((6, 3)).tolist(),
        "U": np.zeros((6, 3)).tolist(),
        "R": np.zeros((6, 3)).tolist(),
        "B": np.zeros((6, 3)).tolist(),
        "L": np.zeros((6, 3)).tolist(),
        "D": np.zeros((6, 3)).tolist()
    }

    facelet_hsv["F"][0], facelet_hsv["R"][1], facelet_hsv["F"][2], facelet_hsv["R"][
        3], facelet_hsv["F"][4], facelet_hsv["R"][5] = camera.get_raw_hsv("1_FRFRFR")
    logging.debug(scanstr.format("FR", "FRFRFR"))

    motors.execute("F2")
    _, facelet_hsv["L"][1], _, facelet_hsv["L"][3], _, facelet_hsv["L"][5] = camera.get_raw_hsv(
        "2__L_L_L")
    logging.debug(scanstr.format("_L", "_L_L_L"))

    motors.execute("F")
    _, facelet_hsv["D"][1], _, facelet_hsv["D"][3], _, facelet_hsv["D"][5] = camera.get_raw_hsv(
        "3__D_D_D")
    logging.debug(scanstr.format("_D", "_D_D_D"))

    motors.execute("F R")  # origin, then R.
    facelet_hsv["D"][0], _, facelet_hsv["D"][2], _, facelet_hsv["D"][4], _ = camera.get_raw_hsv(
        "4_D_D_D_")
    logging.debug(scanstr.format("D_", "D_D_D_"))

    motors.execute("R' U R'")  # origin, then U R"
    facelet_hsv["U"][0], facelet_hsv["B"][1], facelet_hsv["U"][2], facelet_hsv["B"][
        3], facelet_hsv["U"][4], facelet_hsv["B"][5] = camera.get_raw_hsv("5_UBUBUB")
    logging.debug(scanstr.format("UB", "UBUBUB"))

    motors.execute("R U' R U F")  # origin, then R U F
    facelet_hsv["R"][0], facelet_hsv["F"][1], facelet_hsv["R"][2], facelet_hsv["F"][
        3], facelet_hsv["R"][4], facelet_hsv["F"][5] = camera.get_raw_hsv("6_RFRFRF")
    logging.debug(scanstr.format("RF", "RFRFRF"))

    motors.execute("F' U' R' U' F")  # origin, then U' F
    facelet_hsv["L"][0], _, facelet_hsv["L"][2], _, facelet_hsv["L"][4], _ = camera.get_raw_hsv(
        "7_L_L_L_")
    logging.debug(scanstr.format("L_", "L_L_L_"))

    motors.execute("F' U' F")
    facelet_hsv["B"][0], facelet_hsv["U"][1], facelet_hsv["B"][2], facelet_hsv["U"][
        3], facelet_hsv["B"][4], facelet_hsv["U"][5] = camera.get_raw_hsv("8_BUBUBU")
    logging.debug(scanstr.format("BU", "BUBUBU"))

    motors.execute("F' U2")  # back to origin

    # at this point, we"ve scanned all the colors on each facelet.
    # Now lets build the calibration data based on the gathered hsv raw values.
    cal = {}
    min_hsv = np.array([255, 255, 255])
    max_hsv = np.array([0, 0, 0])
    for key in facelet_hsv:
        # note: we don"t account for red overflow here, jsut store the min H larger than the max H
        cal_entry = {}
        for hsv_entry in facelet_hsv[key]:
            min_hsv = np.minimum(min_hsv, hsv_entry)
            max_hsv = np.maximum(max_hsv, hsv_entry)

        cal_entry["min"] = min_hsv
        cal_entry["max"] = max_hsv
        cal[key] = cal_entry

    # collision-detection
    collision_detect(cal)

    retval = {"colors": cal,
              "sample_size": camera.calib_data["sample_size"]}
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
    with open(config_file, "r") as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    logging.basicConfig(
        level=logging.getLevelName(config["app"]["logLevel"]), format=config["app"]["logFormat"])

    motors = MotorController(config)

    c = camera.get_settings()
    s = calibrate(motors)
    obj = {"camera": c, "calib": s}
    yaml_text = yaml.dump(obj, default_flow_style=True)

    if args["F"]:
        with open(args["F"], "w") as outfile:
            yaml.dump(obj, outfile, default_flow_style=True)
    else:
        logging.info(yaml_text)
