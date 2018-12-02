"""
    Functions for scanning, evaluating and representing the state of a cube. Depends on camera.py and stepper.py
    to control the camera and stepper motors, respectively.
"""

import logging
import numpy as np
import math
import yaml
from PIL import Image, ImageDraw

import stepper
import camera
from config import cfg

logging.basicConfig(
    level=logging.getLevelName(cfg['app']['logLevel']), format=cfg['app']['logFormat'])


colorSampleCoords = cfg['cam']['colorSampleCoords']
calib_file = cfg['cam']['calibration']
calib = {}
with open(calib_file, 'r') as ymlfile:
    calib = yaml.load(ymlfile)

camera = camera.Camera(cfg['cam']['camera_deviceID'],
                       colorSampleCoords, calib)
# camera_BL = Camera(cfg['cam']['camera_BL_deviceName'],
#                    colorSampleCoords["back"],calib["calib"]["colors_BL"])

warmup_delay_ms = cfg['cam']['warmup_delay_ms']

DEFAULT_STATE = {
    'F': np.full(9, "F").tolist(),
    'B': np.full(9, "B").tolist(),
    'L': np.full(9, "L").tolist(),
    'R': np.full(9, "R").tolist(),
    'U': np.full(9, "U").tolist(),
    'D': np.full(9, "D").tolist()
}


def debug(str, wait=False):
    print(str)
    if wait:
        input("press any key to continue.")


def scan_state():
    """
    Scan the current state of the cube, and return a map of <facename:array<facename>> to represent the cube state.
    Cube state is represented like:

                  |------------|
                  |*U0**U1**U2*|
                  |------------|
                  |*U3**U4**U5*|
                  |------------|
                  |*U6**U7**U8*|
     |------------|============|------------|------------|
     |*L0**L1**L2*|*F0**F1**F2*|*R0**R1**R2*|*B0**B1**B2*|
     |------------|------------|------------|------------|
     |*L3**L4**L5*|*F3**F4**F5*|*R3**R4**R5*|*B3**B4**B5*|
     |------------|------------|------------|------------|
     |*L6**L7**L8*|*F6**F7**F8*|*R6**R7**R8*|*B6**B7**B8*|
     |------------|============|------------|------------|
                  |*D0**D1**D2*|
                  |------------|
                  |*D3**D4**D5*|
                  |------------|
                  |*D6**D7**D8*|
                  |------------|
    """

    state = dict(DEFAULT_STATE)

    state['F'][2], state['R'][0], state['F'][5], state['R'][3], state['F'][8], state['R'][6] = camera.get_colors()

    stepper.execute('F')
    state['F'][0], state['U'][6], state['F'][1], state['U'][7], _, state['U'][8] = camera.get_colors()

    stepper.execute('F')
    state['F'][6], state['L'][8], state['F'][3], state['L'][5], _, state['L'][2] = camera.get_colors()

    stepper.execute('F')
    _, state['D'][2], state['F'][7], state['D'][1], _, state['D'][0] = camera.get_colors()

    stepper.execute('F R')  # origin, then R
    _, _, state['D'][5], state['R'][7], state['D'][8], state['R'][8] = camera.get_colors()

    stepper.execute('R')
    state['B'][6], _, state['B'][3], state['R'][5], state['B'][0], state['R'][2] = camera.get_colors()

    stepper.execute('R')
    state['U'][2], _, state['U'][5], state['R'][1], _, _ = camera.get_colors()

    stepper.execute("R B' U R'")  # origin, then B' U R'
    state['L'][6], state['B'][8], state['L'][3], state['B'][5], state['L'][0], state['B'][2] = camera.get_colors()

    stepper.execute("R U' B L' F2")  # origin, then L' F2
    state['D'][7], _, state['D'][4], _, _, _ = camera.get_colors()

    stepper.execute("F2 L")
    return state


# def calibrate():
#     """
#     Scan a (currently solved) cube, and use the mean of the resulting color values as calibrated color centers for each edge / corner facelet.
#     Generate radius based on the known values encountered.

#     WE ASSUME: That the cube is fully solved, and present in a known orientation (Orange face front, Yellow face up).
#     """

#     # TODO: Allow for other orientations of the cube, passed as a parameter.

#     # colors, in BGR format.

#     colors = {
#         'O': np.zeros((6, 3)).tolist(),
#         'R': np.zeros((6, 3)).tolist(),
#         'G': np.zeros((6, 3)).tolist(),
#         'B': np.zeros((6, 3)).tolist(),
#         'Y': np.zeros((6, 3)).tolist(),
#         'W': np.zeros((6, 3)).tolist()
#     }

#     # scan front

#     colors['O'][0], colors['B'][1], colors['O'][2], colors['B'][
#         3], colors['O'][4], colors['B'][5] = camera.get_raw_colors("1_OBOBOB")

#     debug("scanning {0}: {1}".format("FR", "OBOBOB"))

#     stepper.execute("F2")
#     _, colors['G'][1], _, colors['G'][3], _, colors['G'][5] = camera.get_raw_colors(
#         "2__G_G_G")
#     debug("scanning {0}: {1}".format("FR", "_G_G_G"))

#     stepper.execute("F")
#     _, colors['W'][1], _, colors['W'][3], _, colors['W'][5] = camera.get_raw_colors(
#         "3__W_W_W")
#     debug("scanning {0}: {1}".format("FR", "_W_W_W"))

#     stepper.execute("F R")  # origin, then R.
#     colors['W'][0], _, colors['W'][2], _, colors['W'][4], _ = camera.get_raw_colors(
#         "4_W_W_W_")
#     debug("scanning {0}: {1}".format("FR", "W_W_W_"))

#     stepper.execute("R' U R'")  # origin, then U R'
#     colors['Y'][0], colors['R'][1], colors['Y'][2], colors['R'][
#         3], colors['Y'][4], colors['R'][5] = camera.get_raw_colors("5__YRYRYR")
#     debug("scanning {0}: {1}".format("FR", "YRYRYR"))

#     stepper.execute("R U' R U F")  # origin, then R U F
#     colors['B'][0], colors['O'][1], colors['B'][2], colors['O'][
#         3], colors['B'][4], colors['O'][5] = camera.get_raw_colors("6_BOBOBO")
#     debug("scanning {0}: {1}".format("FR", "BOBOBO"))

#     stepper.execute("F' U' R' U' F")  # origin, then U' F
#     colors['G'][0], _, colors['G'][2], _, colors['G'][4], _ = camera.get_raw_colors(
#         "7_G_G_G_")
#     debug("scanning {0}: {1}".format("FR", "G_G_G_"))

#     stepper.execute("F' U' F")
#     colors['R'][0], colors['Y'][1], colors['R'][2], colors['Y'][
#         3], colors['R'][4], colors['Y'][5] = camera.get_raw_colors("8_RYRYRY")
#     debug("scanning {0}: {1}".format("FR", "RYRYRY"))

#     stepper.execute("F' U2")  # back to origin

#     # at this point, we've scanned all the colors on each facelet.
#     # Now lets build the calibration data based on the gathered data.
#     cal = {}
#     for key in colors:
#         cal_entry = {}
#         face = colors[key]
#         arr = np.sum(np.array(face), axis=0)
#         arr = [x / len(face) for x in arr]
#         radius = 2.0       # start with a reasonable default value.
#         for facelet in face:
#             diff = [abs(a_i - b_i) for a_i, b_i in zip(arr, facelet)]
#             dist = math.sqrt((diff[0]-arr[0])**2 +
#                              (diff[1] - arr[1]) ** 2 + (diff[2] - arr[2]) ** 2)
#             if dist > radius or radius == 0.0:
#                 radius = dist  # euclidean distance from the average to the outlyingest color sample

#         cal_entry["rgb"] = colors[key]
#         cal_entry["radius"] = 20.0  # radius
#         cal[key] = cal_entry

#     # collision-detection, to assert that no two non-equivalent color pseudo-spheres collide (e.g.:
#     # Is there a risk that a blue facelet could be mistaken for a yellow facelet,
#     # using any of the "blue" colors-plus-radius, and any of the "yellow"
#     # colors-plus-radius). Rough upper-bound is every facelet compared to every other facelet of a
#     # different color, for each camera: 2 * 36 * (1+2+3+4+5) = 1080 comparisons.

#     ccount = 1

#     compared = {"R": [], "O": [], "Y": [], "G": [], "B": [], "W": []}
#     errors = []
#     for key1 in cal:  # 6
#         colors1 = cal[key1]["rgb"]
#         for key2 in cal:  # 5, 4, 3, 2, 1
#             compared[key1].append(key2)
#             if key2 != key1 and key1 not in compared[key2]:
#                 colors2 = cal[key2]["rgb"]
#                 # only test against colors in the same position.
#                 for i in range(6):
#                     clr1 = colors1[i]
#                     clr2 = colors2[i]
#                     logging.info("#{4}: Testing {0}:{1} against {2}:{3}".format(
#                         key1, clr1, key2, clr2, ccount))
#                     ccount += 1
#                     dist = math.sqrt(
#                         (clr1[0] - clr2[0]) ** 2 + (clr1[1] - clr2[1]) ** 2 + (clr1[2] - clr2[2]) ** 2)
#                     if dist < cal[key1]["radius"] or dist < cal[key2]["radius"]:
#                         cal[key1]["radius"] = min(
#                             cal[key1]["radius"], round(dist, 2))
#                         cal[key2]["radius"] = min(
#                             cal[key2]["radius"], round(dist, 2))

#                         errors.append(
#                             {
#                                 "color1": key1,
#                                 "radius1": cal[key1]["radius"],
#                                 "rgb1": clr1,
#                                 "color2": key2,
#                                 "radius2": cal[key2]["radius"],
#                                 "rgb2": clr2,
#                                 "dist": dist,
#                             }
#                         )
#         logging.info("compared: {0}".format(compared))

#     if len(errors) > 0:
#         logging.warn("-----------------------------------------------")
#         logging.warn(
#             "There were collisions in the color calibration, and radii were automatically adjusted:")
#         for err in errors:
#             logging.warn("\t{0}".format(err))
#         logging.warn("-----------------------------------------------")

#     retval = {"colors": cal, "sample_size": camera.calib_data["sample_size"]}
#     return retval


def get_state_string(state=None):
    """
    Given a map of <faces,array<facelet>>, representing the cube state, return a
    string representation, according to the order U1, U2, U3, U4, U5, U6, U7, U8, U9, R1, R2,
    R3, R4, R5, R6, R7, R8, R9, F1, F2, F3, F4, F5, F6, F7, F8, F9, D1, D2, D3, D4,
    D5, D6, D7, D8, D9, L1, L2, L3, L4, L5, L6, L7, L8, L9, B1, B2, B3, B4, B5, B6,
    B7, B8, B9

    Example state: "DLRUULBDFLFFDRBBRRDLUFFFBRDUDLRDFRDULBRLLUBULDBFRBUFBU"
    """
    if state is None:
        state = scan_state()

    retval = "".join(state['U']) \
        + "".join(state['R']) \
        + "".join(state['F']) \
        + "".join(state['D']) \
        + "".join(state['L']) \
        + "".join(state['B'])

    # test for a valid cube state.
    if len(retval) != 54:
        logging.error("Invalid Cube State! (not enough faces!)")
        retval = ""

    if (len(state['U']) != 9 or len(state['R']) != 9 or len(state['F']) != 9 or len(state['D']) != 9 or len(state['L']) != 9 or len(state['B']) != 9):
        logging.error('Invalid Cube State! (inconsistent colors: U={:d}, R={:d}, F={:d}, D={:d}, L={:d}, B={:d})'.format(
            len(state['U']), len(state['R']), len(state['F']), len(state['D']), len(state['L']), len(state['B'])))
        retval = ""

    if state['U'][4] != 'U' or state['R'][4] != 'R' or state['F'][4] != 'F' or state['D'][4] != 'D' or state['L'][4] != 'L' or state['B'][4] != 'B':
        logging.error('Invalid Cube State! (Center facelets are not correct)')
        retval = ""

    return retval


def get_state_img(state=None):
    """
    Given a state representation of the cube, dynamically generate a cube image, represented as a "Cross".

    e.g.:
        |---|
        |   |
    |---|---|---|---|
    |   |   |   |   |
    |---|---|---|---|
        |   |
        |---|

    """

    colormap = {
        "F": (255, 165, 0, 255),
        "U": (255, 255, 0, 255),
        "R": (0, 0, 255, 255),
        "B": (255, 0, 0, 255),
        "L": (0, 255, 0, 255),
        "D": (255, 255, 255, 255)
    }

    if state is None:
        state = DEFAULT_STATE  # scan_state()

    cubesize = 8
    img = Image.new('RGBA', (12*cubesize+1, 9*cubesize+1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # draw the empty cube.
    xb = 3 * cubesize
    yb = 0 * cubesize
    i = 0
    for y in range(3):
        for x in range(3):
            draw.rectangle([(xb + x * cubesize, yb + y * cubesize),
                            (xb + (x+1) * cubesize, yb + (y + 1) * cubesize)],
                           fill=colormap[state["U"][i]],
                           outline=(0, 0, 0, 255), width=1)
            i += 1

    xb = 0 * cubesize
    yb = 3 * cubesize
    i = 0
    for y in range(3):
        for x in range(3):
            draw.rectangle([(xb + x * cubesize, yb + y * cubesize),
                            (xb + (x+1) * cubesize, yb + (y + 1) * cubesize)],
                           fill=colormap[state["L"][i]],
                           outline=(0, 0, 0, 255), width=1)
            i += 1

    xb = 3 * cubesize
    yb = 3 * cubesize
    i = 0
    for y in range(3):
        for x in range(3):
            draw.rectangle([(xb + x * cubesize, yb + y * cubesize),
                            (xb + (x+1) * cubesize, yb + (y + 1) * cubesize)],
                           fill=colormap[state["F"][i]],
                           outline=(0, 0, 0, 255), width=1)
            i += 1

    xb = 6 * cubesize
    yb = 3 * cubesize
    i = 0
    for y in range(3):
        for x in range(3):
            draw.rectangle([(xb + x * cubesize, yb + y * cubesize),
                            (xb + (x+1) * cubesize, yb + (y + 1) * cubesize)],
                           fill=colormap[state["R"][i]],
                           outline=(0, 0, 0, 255), width=1)
            i += 1

    xb = 9 * cubesize
    yb = 3 * cubesize
    i = 0
    for y in range(3):
        for x in range(3):
            draw.rectangle([(xb + x * cubesize, yb + y * cubesize),
                            (xb + (x+1) * cubesize, yb + (y + 1) * cubesize)],
                           fill=colormap[state["B"][i]],
                           outline=(0, 0, 0, 255), width=1)
            i += 1

    xb = 3 * cubesize
    yb = 6 * cubesize
    i = 0
    for y in range(3):
        for x in range(3):
            draw.rectangle([(xb + x * cubesize, yb + y * cubesize),
                            (xb + (x+1) * cubesize, yb + (y + 1) * cubesize)],
                           fill=colormap[state["D"][i]],
                           outline=(0, 0, 0, 255), width=1)
            i += 1

    return img
