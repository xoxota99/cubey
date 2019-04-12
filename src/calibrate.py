import numpy as np
import logging
import yaml
import math
import sys

from cubey import camera
from cubey.stepper import MotorController

config_file = "config.yaml"
config = {}
with open(config_file, 'r') as ymlfile:
    config = yaml.load(ymlfile)

logging.basicConfig(
    level=logging.getLevelName(config['app']['logLevel']), format=config['app']['logFormat'])

colorSampleCoords = config['cam']['colorSampleCoords']
calib_file = config['cam']['calibration']
calib = {}
with open(calib_file, 'r') as ymlfile:
    calib = yaml.load(ymlfile)

camera = camera.Camera(config, calib)


def calibrate(motors):
    """
    Scan a (currently solved) cube, and use the mean of the resulting color values as calibrated color centers for each edge / corner facelet.
    Generate radius based on the known values encountered.

    WE ASSUME: That the cube is fully solved, and present in a known orientation (Orange face front, Yellow face up).
    """

    # colors, in BGR format.

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
        3], colors['O'][4], colors['B'][5] = camera.get_raw_colors("1_OBOBOB")

    logging.debug("scanning {0}: {1}".format("FR", "OBOBOB"))

    motors.execute("F2")
    _, colors['G'][1], _, colors['G'][3], _, colors['G'][5] = camera.get_raw_colors(
        "2__G_G_G")
    logging.debug("scanning {0}: {1}".format("FR", "_G_G_G"))

    motors.execute("F")
    _, colors['W'][1], _, colors['W'][3], _, colors['W'][5] = camera.get_raw_colors(
        "3__W_W_W")
    logging.debug("scanning {0}: {1}".format("FR", "_W_W_W"))

    motors.execute("F R")  # origin, then R.
    colors['W'][0], _, colors['W'][2], _, colors['W'][4], _ = camera.get_raw_colors(
        "4_W_W_W_")
    logging.debug("scanning {0}: {1}".format("FR", "W_W_W_"))

    motors.execute("R' U R'")  # origin, then U R'
    colors['Y'][0], colors['R'][1], colors['Y'][2], colors['R'][
        3], colors['Y'][4], colors['R'][5] = camera.get_raw_colors("5__YRYRYR")
    logging.debug("scanning {0}: {1}".format("FR", "YRYRYR"))

    motors.execute("R U' R U F")  # origin, then R U F
    colors['B'][0], colors['O'][1], colors['B'][2], colors['O'][
        3], colors['B'][4], colors['O'][5] = camera.get_raw_colors("6_BOBOBO")
    logging.debug("scanning {0}: {1}".format("FR", "BOBOBO"))

    motors.execute("F' U' R' U' F")  # origin, then U' F
    colors['G'][0], _, colors['G'][2], _, colors['G'][4], _ = camera.get_raw_colors(
        "7_G_G_G_")
    logging.debug("scanning {0}: {1}".format("FR", "G_G_G_"))

    motors.execute("F' U' F")
    colors['R'][0], colors['Y'][1], colors['R'][2], colors['Y'][
        3], colors['R'][4], colors['Y'][5] = camera.get_raw_colors("8_RYRYRY")
    logging.debug("scanning {0}: {1}".format("FR", "RYRYRY"))

    motors.execute("F' U2")  # back to origin

    # at this point, we've scanned all the colors on each facelet.
    # Now lets build the calibration data based on the gathered data.
    cal = {}
    for key in colors:
        cal_entry = {}
        face = colors[key]
        arr = np.sum(np.array(face), axis=0)
        arr = [x / len(face) for x in arr]
        radius = 2.0       # start with a reasonable default value.
        for facelet in face:
            diff = [abs(a_i - b_i) for a_i, b_i in zip(arr, facelet)]
            dist = math.sqrt((diff[0]-arr[0])**2 +
                             (diff[1] - arr[1]) ** 2 + (diff[2] - arr[2]) ** 2)
            if dist > radius or radius == 0.0:
                radius = dist  # euclidean distance from the average to the outlyingest color sample

        cal_entry["rgb"] = colors[key]
        cal_entry["radius"] = 20.0  # radius
        cal[key] = cal_entry

    # collision-detection, to assert that no two non-equivalent color pseudo-spheres collide (e.g.:
    # Is there a risk that a blue facelet could be mistaken for a yellow facelet,
    # using any of the "blue" colors-plus-radius, and any of the "yellow"
    # colors-plus-radius). Rough upper-bound is every facelet compared to every other facelet of a
    # different color, for each camera: 2 * 36 * (1+2+3+4+5) = 1080 comparisons.

    ccount = 1

    compared = {"R": [], "O": [], "Y": [], "G": [], "B": [], "W": []}
    errors = []
    for key1 in cal:  # 6
        colors1 = cal[key1]["rgb"]
        for key2 in cal:  # 5, 4, 3, 2, 1
            compared[key1].append(key2)
            if key2 != key1 and key1 not in compared[key2]:
                colors2 = cal[key2]["rgb"]
                # only test against colors in the same position.
                for i in range(6):
                    clr1 = colors1[i]
                    clr2 = colors2[i]
                    logging.info("#{4}: Testing {0}:{1} against {2}:{3}".format(
                        key1, clr1, key2, clr2, ccount))
                    ccount += 1
                    dist = math.sqrt(
                        (clr1[0] - clr2[0]) ** 2 + (clr1[1] - clr2[1]) ** 2 + (clr1[2] - clr2[2]) ** 2)
                    if dist < cal[key1]["radius"] or dist < cal[key2]["radius"]:
                        cal[key1]["radius"] = min(
                            cal[key1]["radius"], round(dist, 2))
                        cal[key2]["radius"] = min(
                            cal[key2]["radius"], round(dist, 2))

                        errors.append(
                            {
                                "color1": key1,
                                "radius1": cal[key1]["radius"],
                                "rgb1": clr1,
                                "color2": key2,
                                "radius2": cal[key2]["radius"],
                                "rgb2": clr2,
                                "dist": dist,
                            }
                        )
        logging.info("compared: {0}".format(compared))

    if len(errors) > 0:
        logging.warn("-----------------------------------------------")
        logging.warn(
            "There were collisions in the color calibration, and radii were automatically adjusted:")
        for err in errors:
            logging.warn("\t{0}".format(err))
        logging.warn("-----------------------------------------------")

    retval = {"colors": cal, "sample_size": camera.calib_data["sample_size"]}
    return retval


def process_args(argv):
    if len(argv) > 1:
        retval = {}
        pName = ""
        for i, arg in enumerate(argv):
            if i % 2 == 0:
                pName = arg
            else:
                retval[pName] = arg
                pName = ""
    return retval


if __name__ == "__main__":
    args = process_args(sys.argv)

    config_file = "config.yaml"
    config = {}
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)

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
