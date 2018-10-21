import os
import subprocess
import logging
import stepper
import numpy as np
import time
import random
from cam import Camera
from config import cfg

logging.basicConfig(
    level=logging.getLevelName(cfg['app']['logLevel']), format=cfg['app']['logFormat'])

CMD = cfg['app']['solverCMD']

camera_FR = Camera(cfg, cfg['app']['camera_FR_deviceName'])
camera_BL = Camera(cfg, cfg['app']['camera_BL_deviceName'])


def solve(t=None):
    if t is None:
        t = get_state_string(scan_state())

    return subprocess.check_output([CMD, t], stderr=open(os.devnull, 'wb')).strip()


# Record cube state, according to:
#
#              |------------|
#              |*U0**U1**U2*|
#              |------------|
#              |*U3**U4**U5*|
#              |------------|
#              |*U6**U7**U8*|
# |------------|============|------------|------------|
# |*L0**L1**L2*|*F0**F1**F2*|*R0**R1**R2*|*B0**B1**B2*|
# |------------|------------|------------|------------|
# |*L3**L4**L5*|*F3**F4**F5*|*R3**R4**R5*|*B3**B4**B5*|
# |------------|------------|------------|------------|
# |*L6**L7**L8*|*F6**F7**F8*|*R6**R7**R8*|*B6**B7**B8*|
# |------------|============|------------|------------|
#              |*D0**D1**D2*|
#              |------------|
#              |*D3**D4**D5*|
#              |------------|
#              |*D6**D7**D8*|
#              |------------|
#
def scan_state():
    # initialize state.

    state = {
        'F': np.full(9, "F"),
        'B': np.full(9, "B"),
        'L': np.full(9, "L"),
        'R': np.full(9, "R"),
        'U': np.full(9, "U"),
        'D': np.full(9, "D")
    }

    # scan front
    logging.info("Scanning FRONT")

    state['F'][2], state['R'][0], state['F'][5], state['R'][3], state['F'][8], state['R'][6] = camera_FR.get_colors()

    stepper.rot_90(stepper.FRONT)
    state['F'][0], state['U'][6], state['F'][1], state['U'][7], _, state['U'][8] = camera_FR.get_colors()

    stepper.rot_90(stepper.FRONT)
    state['F'][6], state['L'][8], state['F'][3], state['L'][5], _, state['L'][2] = camera_FR.get_colors()

    stepper.rot_90(stepper.FRONT)
    _, state['D'][2], state['F'][7], state['D'][1], _, state['D'][0] = camera_FR.get_colors()

    stepper.rot_90(stepper.FRONT)   # back to origin

    # scan right
    logging.info("Scanning RIGHT")
    stepper.rot_90(stepper.RIGHT)
    _, _, state['D'][5], state['R'][7], state['D'][8], state['R'][8] = camera_FR.get_colors()

    stepper.rot_90(stepper.RIGHT)
    state['B'][6], _, state['B'][3], state['R'][5], state['B'][0], state['R'][2] = camera_FR.get_colors()

    stepper.rot_90(stepper.RIGHT)
    state['U'][2], _, state['U'][5], state['R'][1], _, _ = camera_FR.get_colors()

    stepper.rot_90(stepper.RIGHT)  # back to origin

    # scan back
    logging.info("Scanning BACK")
    state['B'][2], state['L'][0], state['B'][5], state['L'][3], state['B'][8], state['L'][6] = camera_BL.get_colors()

    stepper.rot_90(stepper.BACK)
    _, _, state['B'][1], state['U'][1], _, state['U'][0] = camera_BL.get_colors()

    # skip one edge. We've got the data already.

    stepper.rot_180(stepper.BACK)
    _, state['D'][6], state['B'][7], state['D'][7], _, _ = camera_BL.get_colors()

    stepper.rot_90(stepper.BACK)   # back to origin

    # scan left
    logging.info("Scanning LEFT")
    stepper.rot_90(stepper.LEFT)
    _, _, state['D'][3], state['L'][7], _, _ = camera_BL.get_colors()

    # skip one edge. We've got the data already.

    stepper.rot_180(stepper.RIGHT)
    _, _, state['U'][3], state['L'][1], _, _ = camera_BL.get_colors()

    stepper.rot_90(stepper.RIGHT)  # back to origin

    return state


def get_state_string(state):
    """ Cube state, according to the order U1, U2, U3, U4, U5, U6, U7, U8, U9, R1, R2,
    R3, R4, R5, R6, R7, R8, R9, F1, F2, F3, F4, F5, F6, F7, F8, F9, D1, D2, D3, D4,
    D5, D6, D7, D8, D9, L1, L2, L3, L4, L5, L6, L7, L8, L9, B1, B2, B3, B4, B5, B6,
    B7, B8, B9
    """
    return "".join(state['U']) \
        + "".join(state['R']) \
        + "".join(state['F']) \
        + "".join(state['D']) \
        + "".join(state['L']) \
        + "".join(state['B'])


def scramble():
    recipe = ""
    move_count = random.randint(20, 41)

    for _ in range(move_count):
        move = random.choice(stepper.STEP_NAME)
        add = random.randint(0, 3)
        if add == 1:
            move = move + "'"
        elif add == 2:
            move = "2" + move

        recipe = recipe + move + " "

    print("Random Scramble: " + recipe)
    stepper.execute(recipe)


# scan the cube, get a solution from kociemba, then execute it on the robot.
if __name__ == "__main__":

    print("Scanning...")
    t0 = int(round(time.time() * 1000))
    state_str = get_state_string(scan_state())
    t1 = int(round(time.time() * 1000))
    print("Scanned state: " + state_str)

    print("Solving...")
    t2 = int(round(time.time() * 1000))
    solution = solve(state_str)
    t3 = int(round(time.time() * 1000))
    print("Solution: " + solution)

    print("Executing...")
    t4 = int(round(time.time() * 1000))
    stepper.execute(solution)
    t5 = int(round(time.time() * 1000))

    print('Scan time: {:d}ms'.format(t1-t0))
    print('Solve time: {:d}ms'.format(t3-t2))
    print('Execution time: {:d}ms'.format(t5-t4))