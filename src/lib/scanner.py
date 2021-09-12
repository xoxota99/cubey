import logging
import numpy as np
import yaml

from PIL import Image, ImageDraw
from lib.camera import Camera

"""
    Functions for scanning, evaluating and representing the state of a cube. Depends on camera.py and stepper.py
    to control the camera and stepper motors, respectively.
"""

# Default state of the cube, fully solved.
SOLVED_STATE = {
    'F': np.full(9, "F").tolist(),
    'B': np.full(9, "B").tolist(),
    'L': np.full(9, "L").tolist(),
    'R': np.full(9, "R").tolist(),
    'U': np.full(9, "U").tolist(),
    'D': np.full(9, "D").tolist()
}


def get_state_from_string(str):
    # URFDLB
    state = dict(SOLVED_STATE)  # Initialize to fully solved.
    j = 0
    for face in ["U", "R", "F", "D", "L", "B"]:
        for i in range(9):
            state[face][i] = str[j]
            j += 1
    return state


def get_state_img(state):
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

    palette = {
        "F": (255, 165, 0, 255),   # Front/Orange
        "U": (255, 255, 0, 255),   # Up/Yellow
        "R": (0, 0, 255, 255),     # Right/Blue
        "B": (255, 0, 0, 255),     # Back/Red
        "L": (0, 255, 0, 255),     # Left/Green
        "D": (255, 255, 255, 255)  # Down/White
    }

    if isinstance(state, str):
        # convert to state dict
        state = get_state_from_string(state)

    facelet_pixel_size = 8
    img = Image.new('RGBA', (12 * facelet_pixel_size + 1, 9 *
                    facelet_pixel_size + 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    face_coords = [
        [3, 0],
        [0, 3],
        [3, 3],
        [6, 3],
        [9, 3],
        [3, 6]
    ]

    for i, face in enumerate(["U", "L", "F", "R", "B", "D"]):
        xb = face_coords[i][0] * facelet_pixel_size
        yb = face_coords[i][1] * facelet_pixel_size
        for y in range(3):
            for x in range(3):
                draw.rectangle([(xb + x * facelet_pixel_size, yb + y * facelet_pixel_size),
                                (xb + (x + 1) * facelet_pixel_size, yb + (y + 1) * facelet_pixel_size)],
                               fill=palette[state[face][y * 3 + x]],
                               outline=(0, 0, 0, 255), width=1)
    return img


class Scanner:
    """
    The Scanner class uses the camera to "scan" the state of the cube.
    This scanning process is very sensitive to lighting conditions.
    """

    def __init__(self, config):
        self.config = config

        calib_file = "../" + config['cam']['calibration']
        calib = {}
        with open(calib_file, 'r') as ymlfile:
            calib = yaml.load(ymlfile, Loader=yaml.FullLoader)

        self.camera = Camera(config, calib)

    def scan_state(self, motors):
        """
        Scan the current state of the cube, and return a map of <facename:array<facename>> to represent the cube state.
        Cube state is represented like:

                     |------------|
                     |*U0**U1**U2*|
                     |------------|
                     |*U3**U4**U5*|
                     |------------|
                     |*U6**U7**U8*|
        |------------|------------|------------|------------|
        |*L0**L1**L2*|*F0**F1**F2*|*R0**R1**R2*|*B0**B1**B2*|
        |------------|------------|------------|------------|
        |*L3**L4**L5*|*F3**F4**F5*|*R3**R4**R5*|*B3**B4**B5*|
        |------------|------------|------------|------------|
        |*L6**L7**L8*|*F6**F7**F8*|*R6**R7**R8*|*B6**B7**B8*|
        |------------|------------|------------|------------|
                     |*D0**D1**D2*|
                     |------------|
                     |*D3**D4**D5*|
                     |------------|
                     |*D6**D7**D8*|
                     |------------|

        The camera is always pointed at the edge <F2-R0-F5-R3-F8-R6>. We obtain the entire cube state by getting the
        colors of all facelets on that edge, then rotating the cube through a predetermined sequence, such that all
        edge facelets rotate through that edge.
        """

        state = dict(SOLVED_STATE)  # Initialize to fully solved.

        # pylint: disable=unbalanced-tuple-unpacking
        state['F'][2], state['R'][0], state['F'][5], state['R'][3], state['F'][8], state['R'][6] = self.camera.get_faces()

        motors.execute('F')     # rotate front face clockwise
        state['F'][0], state['U'][6], state['F'][1], state['U'][7], _, state['U'][8] = self.camera.get_faces()

        motors.execute('F')
        state['F'][6], state['L'][8], state['F'][3], state['L'][5], _, state['L'][2] = self.camera.get_faces()

        motors.execute('F')
        _, state['D'][2], state['F'][7], state['D'][1], _, state['D'][0] = self.camera.get_faces()

        # front map complete.

        motors.execute('F R')
        _, _, state['D'][5], state['R'][7], state['D'][8], state['R'][8] = self.camera.get_faces()

        motors.execute('R')
        state['B'][6], _, state['B'][3], state['R'][5], state['B'][0], state['R'][2] = self.camera.get_faces()

        motors.execute('R')
        state['U'][2], _, state['U'][5], state['R'][1], _, _ = self.camera.get_faces()

        # right map complete

        motors.execute("R B' U R'")
        state['L'][6], state['B'][8], state['L'][3], state['B'][5], state['L'][0], state['B'][2] = self.camera.get_faces()

        motors.execute("R U' B L' F2")
        state['D'][6], _, state['D'][3], state['L'][7], _, _ = self.camera.get_faces()

        motors.execute("F2 L U R'")
        state['U'][0], _, state['U'][1], state['B'][1], state['U'][2], _ = self.camera.get_faces()

        # up map complete

        motors.execute("R U R'")
        _, _, _, state['L'][1], _, _ = self.camera.get_faces()

        # left map complete

        motors.execute("B R2")
        _, _, state['B'][7], state['D'][7], _, _ = self.camera.get_faces()

        # back and down maps complete

        motors.execute("R2 B' R U2")

        return state

    def get_state_string(self, motors, state=None):
        """
        Given a map of <face,array<facelet>>, representing the cube state, return a
        string representation, according to the order U0, U1, U2, U3, U4, U5, U6, U7, U8, R0, R1,
        R2, R3, R4, R5, R6, R7, R8, F0, F1, F2, F3, F4, F5, F6, F7, F8, D0, D1, D2, D3,
        D4, D5, D6, D7, D8, L0, L1, L2, L3, L4, L5, L6, L7, L8, B0, B1, B2, B3, B4, B5,
        B6, B7, B8

        Example state: "DLRUULBDFLFFDRBBRRDLUFFFBRDUDLRDFRDULBRLLUBULDBFRBUFBU":

                     |------------|
                     |*D **L **R *|
                     |------------|
                     |*U **U **L *|
                     |------------|
                     |*B **D **F *|
        |------------|------------|------------|------------|
        |*L **B **R *|*D **L **U *|*L **F **F *|*D **B **F *|
        |------------|------------|------------|------------|
        |*L **L **U *|*F **F **F *|*D **R **B *|*R **B **U *|
        |------------|------------|------------|------------|
        |*B **U **L *|*B **R **D *|*B **R **R *|*F **B **U *|
        |------------|------------|------------|------------|
                     |*U **D **L *|
                     |------------|
                     |*R **D **F *|
                     |------------|
                     |*R **D **U *|
                     |------------|
        """
        if state is None:
            state = self.scan_state(motors)

        retval = "".join(state['U']) \
            + "".join(state['R']) \
            + "".join(state['F']) \
            + "".join(state['D']) \
            + "".join(state['L']) \
            + "".join(state['B'])

        # fast (imperfect) test for a valid cube state.
        if len(retval) != 54:  # Is the string exactly 54 characters?
            logging.error("Invalid Cube State! (not enough faces!)")
            retval = ""

        if (len(state['U']) != 9 or len(state['R']) != 9 or len(state['F']) != 9 or len(state['D']) != 9 or len(state['L']) != 9 or len(state['B']) != 9):
            # Is each face exactly 9 facelets?
            logging.error('Invalid Cube State! (inconsistent colors: U={:d}, R={:d}, F={:d}, D={:d}, L={:d}, B={:d})'.format(
                len(state['U']), len(state['R']), len(state['F']), len(state['D']), len(state['L']), len(state['B'])))
            retval = ""

        if state['U'][4] != 'U' or state['R'][4] != 'R' or state['F'][4] != 'F' or state['D'][4] != 'D' or state['L'][4] != 'L' or state['B'][4] != 'B':
            # Is the center facelet of each face the same as the face itself? (since center squares can't move)
            logging.error(
                'Invalid Cube State! (Center facelets are not correct)')
            retval = ""

        return retval


if __name__ == "__main__":
    state = "FDUUUDRFFRFFLRLLFFBUDRFBLBBBRDRDRUULLBDFLDRUURBUDBLDLB"

    get_state_img(state).save("{0}.png".format(state))
