import sys
import os
import subprocess
import logging
import stepper
import numpy as np
import cam

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

CMD = './kociemba/solve'

state = {
    'F': np.full(9, "F"),
    'B': np.full(9, "B"),
    'L': np.full(9, "L"),
    'R': np.full(9, "R"),
    'U': np.full(9, "U"),
    'D': np.full(9, "D")
}

# TODO: Fix this.
cam1 = Camera("dev/v4l/by-id/camera1")
cam2 = Camera("dev/v4l/by-id/camera2")


def solve(t=None):
    if t is None:
        t = get_state_string()

    return subprocess.check_output([CMD, t], stderr=open(os.devnull, 'wb')).strip()


# Given a camera reference, take an edge-on picture of a rubik's cube, and evaluate some of the facelets.
# There are two cameras, Front-Right, and Back-Left.
# In the case of the Front-right camera, for example, return a tuple of FURBDL values that refer to the facelets
# in the (zero-based) F2, R0, F5, R3, F8, R6 positions.
def record_state(cam):
    return "F", "R", "F", "R", "F", "R"


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
    # scan front
    logging.info("Scanning FRONT")

    state['F'][2], state['R'][0], state['F'][5], state['R'][3], state['F'][8], state['R'][6] = record_state(
        cam1)

    stepper.rot_90(stepper.FRONT, stepper.CW)
    state['F'][0], state['U'][6], state['F'][1], state['U'][7], _, state['U'][8] = record_state(
        cam1)

    stepper.rot_90(stepper.FRONT, stepper.CW)
    state['F'][6], state['L'][8], state['F'][3], state['L'][5], _, state['L'][2] = record_state(
        cam1)

    stepper.rot_90(stepper.FRONT, stepper.CW)
    _, state['D'][2], state['F'][7], state['D'][1], _, state['D'][0] = record_state(
        cam1)

    stepper.rot_90(stepper.FRONT, stepper.CW)   # back to origin

    # scan right
    logging.info("Scanning RIGHT")
    stepper.rot_90(stepper.RIGHT, stepper.CW)
    _, _, state['D'][5], state['R'][7], state['D'][8], state['R'][8] = record_state(
        cam1)

    stepper.rot_90(stepper.RIGHT, stepper.CW)
    state['B'][6], _, state['B'][3], state['R'][5], state['B'][0], state['R'][2] = record_state(
        cam1)

    stepper.rot_90(stepper.RIGHT, stepper.CW)
    state['U'][2], _, state['U'][5], state['R'][1], _, _ = record_state(cam1)

    stepper.rot_90(stepper.RIGHT, stepper.CW)  # back to origin

    # scan back
    logging.info("Scanning BACK")
    state['B'][2], state['L'][0], state['B'][5], state['L'][3], state['B'][8], state['L'][6] = record_state(
        cam2)

    stepper.rot_90(stepper.BACK, stepper.CW)
    _, _, state['B'][1], state['U'][1], _, state['U'][0] = record_state(cam2)

    # stepper.rot_90(stepper.BACK, stepper.CW)
    # _, _, _, _, _, _ = record_state(cam2)

    # stepper.rot_90(stepper.BACK, stepper.CW)
    stepper.rot_180(stepper.BACK, stepper.CW)
    _, state['D'][6], state['B'][7], state['D'][7], _, _ = record_state(cam2)

    stepper.rot_90(stepper.BACK, stepper.CW)   # back to origin

    # scan left
    logging.info("Scanning LEFT")
    stepper.rot_90(stepper.LEFT, stepper.CW)
    _, _, state['D'][3], state['L'][7], _, _ = record_state(cam2)

    # stepper.rot_90(stepper.BACK, stepper.CW)
    # _, _, _, _, _, _ = record_state(cam2)

    # stepper.rot_90(stepper.RIGHT, stepper.CW)
    stepper.rot_180(stepper.RIGHT, stepper.CW)
    _, _, state['U'][3], state['L'][1], _, _ = record_state(cam2)

    stepper.rot_90(stepper.RIGHT, stepper.CW)  # back to origin


def get_state_string():
    # Cube state, according to the order U1, U2, U3, U4, U5, U6, U7, U8, U9, R1, R2,
    # R3, R4, R5, R6, R7, R8, R9, F1, F2, F3, F4, F5, F6, F7, F8, F9, D1, D2, D3, D4,
    # D5, D6, D7, D8, D9, L1, L2, L3, L4, L5, L6, L7, L8, L9, B1, B2, B3, B4, B5, B6,
    # B7, B8, B9

    return "".join(state['U']) \
        + "".join(state['R']) \
        + "".join(state['F']) \
        + "".join(state['D']) \
        + "".join(state['L']) \
        + "".join(state['B'])


# scan the cube, get a solution from kociemba, then execute it on the robot.
if __name__ == "__main__":
    scan_state()
    solution = solve()
    stepper.execute(solution)
