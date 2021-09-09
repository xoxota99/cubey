from time import sleep
import logging
import sys

from lib.motorcontroller import MotorController
from lib.solver import Solver

"""
Utility for scrambling / descrambling the cube
"""


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
        level=logging.getLevelName(config['app']['logLevel']), format=config['app']['logFormat'])

    mode = "S"  # scramble by default.

    slv = Solver(config)
    motors = MotorController(config)

    if len(sys.argv) > 1:
        mode = sys.argv[1].upper()

    if mode == "S":  # scramble
        recipe = slv.scramble(20, 30)
        print(recipe)
        motors.execute(recipe)
    elif mode == "D":  # descramble. Optionally provide a recipe.
        if(len(sys.argv) > 2):
            s = sys.argv[2].upper()
        else:
            s = slv.scramble(20, 30)
            print("Scramble: {:s}", s)
            motors.execute(s)
            sleep(1)

        d = descramble(s)
        print("Descramble: {:s}", d)
        motors.execute(d)

    elif mode == "DD":  # INFINITE scramble / descramble.
        while True:
            print()
            s = slv.scramble(20, 30)
            print("Scramble: {:s}", s)
            motors.execute(s)
            sleep(1)

            d = descramble(s)
            print("Descramble: {:s}", d)
            motors.execute(d)
            sleep(1)
