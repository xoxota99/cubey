from time import sleep
import logging
import sys
import random

from lib.motorcontroller import MotorController

"""
Utility for scrambling / descrambling the cube
"""


def scramble(min_scramble_moves, max_scramble_moves):
    """
    Return a move list to scramble the cube.
    The number of moves in the scramble is determined by the config settings app.min_scramble_moves and app.max_scramble_moves
    Example output: "U R' B2 D F' U' D' R F' U2 F' L2 F2 B2 D2 F2 D' F2 B2 U' B2"
    """

    recipe = ""
    move_count = random.randint(min_scramble_moves, max_scramble_moves + 1)
    base = "X"
    last_base = "X"

    for _ in range(move_count):
        while base == last_base:
            # pick a random face
            base = random.choice(["U", "R", "F", "D", "L", "B"])

        last_base = base
        add = random.randint(0, 4)
        xtra = ""

        if add == 1:
            xtra = "'"
        elif add == 2:
            xtra = "2"

        recipe = recipe + base + xtra + " "

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

    return rec2


if __name__ == "__main__":
    import yaml

    config_file = "config.yaml"
    config = {}
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    logging.basicConfig(
        level=logging.getLevelName(config['app']['log_level']), format=config['app']['log_format'])

    mode = "S"  # scramble by default.

    motors = MotorController(config)

    if len(sys.argv) > 1:
        mode = sys.argv[1].upper()

    if mode == "S":  # scramble
        recipe = scramble(20, 30)
        logging.info(recipe)
        motors.execute(recipe)
    elif mode == "D":  # descramble. Optionally provide a recipe.
        if(len(sys.argv) > 2):
            s = sys.argv[2].upper()
        else:
            s = scramble(20, 30)
            logging.info("Scramble: {:s}".format(s))
            motors.execute(s)
            sleep(1)

        d = descramble(s)
        logging.info("Descramble: {:s}".format(d))
        motors.execute(d)

    elif mode == "DD":  # INFINITE scramble / descramble.
        while True:
            logging.info("")
            s = scramble(20, 30)
            logging.info("Scramble: {:s}".format(s))
            motors.execute(s)
            sleep(1)

            d = descramble(s)
            logging.info("Descramble: {:s}".format(d))
            motors.execute(d)
            sleep(1)
