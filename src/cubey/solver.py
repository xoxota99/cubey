import scanner
import os
import subprocess
import stepper
from config import cfg
import random

CMD = cfg['app']['solverCMD']


def solve(cube_state):
    """
    Given a cube state estimation, in the form of a state string, 
    generate a solution by calling the command-line kociemba solver, 
    and return that solution in the form of a string.

    Example input:  "DLRUULBDFLFFDRBBRRDLUFFFBRDUDLRDFRDULBRLLUBULDBFRBUFBU"
    Example output: "U R' B2 D F' U' D' R F' U2 F' L2 F2 B2 D2 F2 D' F2 B2 U' B2"
    """
    return subprocess.check_output([CMD, cube_state], stderr=open(os.devnull, 'wb')).strip()


def scramble(min_scramble_moves, max_scramble_moves):
    """
    Return a move list to scramble the cube. 
    The number of moves in the scramble is determined by the config settings app.min_scramble_moves and app.max_scramble_moves
    Example output: "U R' B2 D F' U' D' R F' U2 F' L2 F2 B2 D2 F2 D' F2 B2 U' B2"
    """
    recipe = ""
    move_count = random.randint(min_scramble_moves, max_scramble_moves+1)
    base = "X"
    last_base = "X"
    for _ in range(move_count):
        while base == last_base:
            base = random.choice(stepper.FACE_NAME)

        last_base = base
        add = random.randint(0, 3)
        xtra = ""

        if add == 1:
            xtra = "'"
        elif add == 2:
            xtra = "2"

        recipe = recipe + base + xtra + " "

    return recipe
