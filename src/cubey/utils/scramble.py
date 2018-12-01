from cubey import stepper
from cubey.config import cfg
from time import sleep
import logging
import random
import os
import sys

logging.basicConfig(
    level=logging.getLevelName(cfg['app']['logLevel']), format=cfg['app']['logFormat'])


def scramble(move_count=20):
    """
    Generate a move list to scramble the cube. Then scramble the cube and return the move list. 

    The number of moves in the scramble is determined by the config settings app.min_scramble_moves and app.max_scramble_moves

    Example output: "U R' B2 D F' U' D' R F' U2 F' L2 F2 B2 D2 F2 D' F2 B2 U' B2"
    """
    recipe = ""
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

    logging.info("Random Scramble: " + recipe)
    stepper.execute(recipe)
    return recipe


def descramble(recipe_str):
    """
    Fun but useless function to take a known scramble recipe, and play it backwards. 
    So we can scramble the cube, then descramble it. Could be useful for running 
    mechanical stress testing ending in a known cube state?
    """
    recipe_arr = recipe_str.split()
    rec2 = ""
    for step in reversed(recipe_arr):
        if("'" in step):
            rec2 += step.replace("'", "") + " "
        elif ("2" not in step):
            rec2 += step + "' "
        else:
            rec2 += step + " "

    logging.info("Descramble: " + rec2)
    stepper.execute(rec2)
    return rec2


if __name__ == "__main__":
    mode = "S"  # scramble by default.

    if len(sys.argv) > 1:
        mode = sys.argv[1].upper()

    if mode == "S":  # scramble
        print(scramble())
    elif mode == "D":  # descramble. Optionally provide a recipe.
        if(len(sys.argv) > 2):
            s = sys.argv[2].upper()
        else:
            s = scramble()
            print("Scramble: {:s}", s)

        d = descramble(s)
        print("Descramble: {:s}", d)
    elif mode == "DD":  # INFINITE scramble / descramble.
        while True:
            print()
            s = scramble()
            print("Scramble: {:s}", s)
            d = descramble(s)
            print("Descramble: {:s}", d)
            sleep(2)
