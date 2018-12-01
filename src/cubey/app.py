# import os
import sys
import logging
# import subprocess
import stepper
import time
# import random
import scanner
import solver
from config import cfg

logging.basicConfig(
    level=logging.getLevelName(cfg['app']['logLevel']), format=cfg['app']['logFormat'])

# MIN_SCRAMBLE_MOVES = cfg['app']['min_scramble_moves']
# MAX_SCRAMBLE_MOVES = cfg['app']['max_scramble_moves']


# def scramble():
#     """
#     Generate a move list to scramble the cube. Then scramble the cube and return the move list.

#     The number of moves in the scramble is determined by the config settings app.min_scramble_moves and app.max_scramble_moves

#     Example output: "U R' B2 D F' U' D' R F' U2 F' L2 F2 B2 D2 F2 D' F2 B2 U' B2"
#     """
#     recipe = ""
#     move_count = random.randint(MIN_SCRAMBLE_MOVES, MAX_SCRAMBLE_MOVES+1)
#     base = "X"
#     last_base = "X"
#     for _ in range(move_count):
#         while base == last_base:
#             base = random.choice(stepper.FACE_NAME)

#         last_base = base
#         add = random.randint(0, 3)
#         xtra = ""

#         if add == 1:
#             xtra = "'"
#         elif add == 2:
#             xtra = "2"

#         recipe = recipe + base + xtra + " "

#     logging.info("Random Scramble: " + recipe)
#     stepper.execute(recipe)
#     return recipe


# def descramble(recipe_str):
#     """
#     Fun but useless function to take a known scramble recipe, and play it backwards.
#     So we can scramble the cube, then descramble it. Could be useful for running
#     mechanical stress testing ending in a known cube state?
#     """
#     recipe_arr = recipe_str.split()
#     rec2 = ""
#     for step in reversed(recipe_arr):
#         if("'" in step):
#             rec2 += step.replace("'", "") + " "
#         elif ("2" not in step):
#             rec2 += step + "' "
#         else:
#             rec2 += step + " "

#     logging.info("Descramble: " + rec2)
#     stepper.execute(rec2)
#     return rec2


def main():
    """scan the cube, get a solution from kociemba, then execute it on the robot."""
    logging.info("Scanning...")
    t0 = round(time.time() * 1000)
    state_str = scanner.get_state_string(scanner.scan_state())
    t1 = round(time.time() * 1000)
    logging.info("Scanned state: " + state_str)

    time.sleep(1)

    logging.info("Solving...")
    t2 = round(time.time() * 1000)
    solution = solver.solve(state_str)
    t3 = round(time.time() * 1000)
    logging.info("Solution: " + solution)

    logging.info("Executing...\n")
    t4 = round(time.time() * 1000)
    stepper.execute(solution)
    t5 = round(time.time() * 1000)

    logging.info('Scan time: {:d}ms'.format(t1-t0))
    logging.info('Solve time: {:d}ms'.format(t3-t2))
    logging.info('Execution time: {:d}ms'.format(t5-t4))

    return(0)


if __name__ == "__main__":
    sys.exit(main())
