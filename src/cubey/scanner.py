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
from camera import Camera

# logging.basicConfig(
#     level=logging.getLevelName(cfg['app']['logLevel']), format=cfg['app']['logFormat'])

# warmup_delay_ms = config['cam']['warmup_delay_ms']

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


class Scanner:
    def __init__(self, config):
        self.config = config

        calib_file = config['cam']['calibration']
        calib = {}
        with open(calib_file, 'r') as ymlfile:
            calib = yaml.load(ymlfile)

        self.camera = Camera(config, calib)

    def scan_state(self):
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

        state['F'][2], state['R'][0], state['F'][5], state['R'][3], state['F'][8], state['R'][6] = self.camera.get_colors()

        stepper.execute('F')
        state['F'][0], state['U'][6], state['F'][1], state['U'][7], _, state['U'][8] = self.camera.get_colors()

        stepper.execute('F')
        state['F'][6], state['L'][8], state['F'][3], state['L'][5], _, state['L'][2] = self.camera.get_colors()

        stepper.execute('F')
        _, state['D'][2], state['F'][7], state['D'][1], _, state['D'][0] = self.camera.get_colors()

        stepper.execute('F R')  # origin, then R
        _, _, state['D'][5], state['R'][7], state['D'][8], state['R'][8] = self.camera.get_colors()

        stepper.execute('R')
        state['B'][6], _, state['B'][3], state['R'][5], state['B'][0], state['R'][2] = self.camera.get_colors()

        stepper.execute('R')
        state['U'][2], _, state['U'][5], state['R'][1], _, _ = self.camera.get_colors()

        stepper.execute("R B' U R'")  # origin, then B' U R'
        state['L'][6], state['B'][8], state['L'][3], state['B'][5], state['L'][0], state['B'][2] = self.camera.get_colors()

        stepper.execute("R U' B L' F2")  # origin, then L' F2
        state['D'][7], _, state['D'][4], _, _, _ = self.camera.get_colors()

        stepper.execute("F2 L")
        return state

    def get_state_string(self, state=None):
        """
        Given a map of <faces,array<facelet>>, representing the cube state, return a
        string representation, according to the order U1, U2, U3, U4, U5, U6, U7, U8, U9, R1, R2,
        R3, R4, R5, R6, R7, R8, R9, F1, F2, F3, F4, F5, F6, F7, F8, F9, D1, D2, D3, D4,
        D5, D6, D7, D8, D9, L1, L2, L3, L4, L5, L6, L7, L8, L9, B1, B2, B3, B4, B5, B6,
        B7, B8, B9

        Example state: "DLRUULBDFLFFDRBBRRDLUFFFBRDUDLRDFRDULBRLLUBULDBFRBUFBU"
        """
        if state is None:
            state = self.scan_state()

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
            logging.error(
                'Invalid Cube State! (Center facelets are not correct)')
            retval = ""

        return retval

    def get_state_img(self, state=None):
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
