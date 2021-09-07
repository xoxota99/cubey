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
    Scan a (currently solved) cube, and use the mean of the resulting color values as calibrated color centers for
    each edge / corner facelet. Generate radius based on the known values encountered.

    ASSUME: That the cube is fully solved, and present in a known orientation (Orange facelets front, Yellow facelets up).

    motors - An instance of MotorController
    """

    scanstr = "scanning edge {0}: {1}"

    # There are six facelets along the scanning edge of the cube. We want the RGB values for each color,
    # at each facelet, so we can recognize it under these lighting conditions later, when scanning the
    # cube. Store RGB values for each facelet / color.
    raw_colors = {
        'O': np.zeros((6, 3)).tolist(),
        'R': np.zeros((6, 3)).tolist(),
        'G': np.zeros((6, 3)).tolist(),
        'B': np.zeros((6, 3)).tolist(),
        'Y': np.zeros((6, 3)).tolist(),
        'W': np.zeros((6, 3)).tolist()
    }

    raw_colors['O'][0], raw_colors['B'][1], raw_colors['O'][2], raw_colors['B'][
        3], raw_colors['O'][4], raw_colors['B'][5] = camera.get_raw_colors("1_OBOBOB")

    logging.debug(scanstr.format("FR", "OBOBOB"))

    motors.execute("U R'")
    raw_colors['Y'][0], raw_colors['R'][1], raw_colors['Y'][2], raw_colors['R'][
        3], raw_colors['Y'][4], raw_colors['R'][5] = camera.get_raw_colors("2_YRYRYR")

    logging.debug(scanstr.format("UB", "YRYRYR"))

    motors.execute("R F")
    raw_colors['B'][0], raw_colors['Y'][1], raw_colors['B'][2], raw_colors['Y'][
        3], raw_colors['B'][4], raw_colors['Y'][5] = camera.get_raw_colors("3_BYBYBY")

    logging.debug(scanstr.format("RU", "BYBYBY"))

    # Blue and Yellow are complete.

    motors.execute("F U' R'")
    raw_colors['W'][0], raw_colors['O'][1], raw_colors['W'][2], raw_colors['O'][
        3], raw_colors['W'][4], raw_colors['O'][5] = camera.get_raw_colors("4_WOWOWO")

    logging.debug(scanstr.format("DF", "WOWOWO"))

    # Orange is complete.

    motors.execute("L2 F2")
    raw_colors['R'][0], raw_colors['G'][1], raw_colors['R'][2], raw_colors['G'][
        3], raw_colors['R'][4], raw_colors['G'][5] = camera.get_raw_colors("5_RGRGRG")

    logging.debug(scanstr.format("BL", "RGRGRG"))

    # Red is complete

    motors.execute("F2 L2 R U F2 D F'")
    raw_colors['G'][0], raw_colors['W'][1], raw_colors['G'][2], raw_colors['W'][
        3], raw_colors['G'][4], raw_colors['W'][5] = camera.get_raw_colors("6_GWGWGW")

    logging.debug(scanstr.format("LD", "GWGWGW"))

    # Green and White are complete.

    motors.execute("F D' U'")  # return to solved state.

    # 6 scans, 24 moves.

    # at this point, we've scanned all the colors on each facelet.
    # Now build the calibration data based on the gathered raw color data.
    cal = {}
    for key in raw_colors:
        cal_entry = {}
        # raw color data for all the facelets of a given color. (size=6)
        facelets = raw_colors[key]

        # sum of r, g, and b values for this color, across all facelets. (size=3)
        rgb_mean = np.sum(np.array(facelets), axis=0)

        # divide the r, g, and b value by the number of facelets (6), obtaining the mean. (size=3)
        rgb_mean = [x / len(facelets) for x in rgb_mean]

        # rgb_deviation is the deviation from the rgb_mean value to the most outlying color sample.

        rgb_deviation = [0.0, 0.0, 0.0]
        for facelet in facelets:
            rgb_diff = [abs(a_i - b_i) for a_i, b_i in zip(rgb_mean, facelet)]
            rgb_deviation = [max(rgb1, rgb2)
                             for rgb1, rgb2 in zip(rgb_diff, rgb_deviation)]

        # raw color data for this color (6 samples)
        cal_entry["rgb"] = raw_colors[key]

        # acceptable deviation, with the raw samples
        cal_entry["radius"] = rgb_deviation

        cal[key] = cal_entry

    # collision-detection, to assert that no two non-equivalent color pseudo-spheres collide (e.g.:
    # Is there a risk that a blue facelet could be mistaken for a yellow facelet, using any of the
    # "blue" colors-plus-radius, and any of the "yellow" colors-plus-radius).
    #
    # Rough upper-bound is every facelet compared to every other facelet of a different color:
    #       6 * (6+5+$+3+2+1) = 126 comparisons.

    ccount = 1

    compared = {"R": [], "O": [], "Y": [], "G": [], "B": [], "W": []}
    errors = []
    for key1 in cal:  # for each color
        # get the six different rgb values for color 1
        colors1 = cal[key1]["rgb"]
        for key2 in cal:  # for each color
            # keep track that we've already compared these two colors.
            compared[key1].append(key2)
            # if it's not the same as color 1, and it hasn't previously been reverse-compared
            if key2 != key1 and key1 not in compared[key2]:
                # get the six different rgb values for color 2
                colors2 = cal[key2]["rgb"]

                # only test against colors in the same facelet position.
                for i in range(6):
                    clr1 = colors1[i]
                    clr2 = colors2[i]
                    logging.info("#{4}: Testing {0}:{1} against {2}:{3}".format(
                        key1, clr1, key2, clr2, ccount))
                    ccount += 1
                    dist = math.sqrt(((clr1[0] - clr2[0]) ** 2)
                                     + ((clr1[1] - clr2[1]) ** 2)
                                     + ((clr1[2] - clr2[2]) ** 2))  # euclidean distance

                    if dist < cal[key1]["radius"] or dist < cal[key2]["radius"]:
                        # these two colors "overlap" somehow.
                        # TODO: This will definitely not work. Taking a single mean for r, g, and b values will mean an outlier in redspace will overlap with another outlier in bluespace.
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
