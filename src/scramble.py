from time import sleep
import logging
import random
import os
import sys
from cubey import stepper
from cubey import solver


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
    import yaml

    config_file = "config.yaml"
    config = {}
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    logging.basicConfig(
        level=logging.getLevelName(config['app']['logLevel']), format=config['app']['logFormat'])

    mode = "S"  # scramble by default.

    slv = solver.Solver(config)

    if len(sys.argv) > 1:
        mode = sys.argv[1].upper()

    if mode == "S":  # scramble
        print(slv.scramble(20, 30))
    elif mode == "D":  # descramble. Optionally provide a recipe.
        if(len(sys.argv) > 2):
            s = sys.argv[2].upper()
        else:
            s = slv.scramble(20, 30)
            print("Scramble: {:s}", s)

        d = descramble(s)
        print("Descramble: {:s}", d)
    elif mode == "DD":  # INFINITE scramble / descramble.
        while True:
            print()
            s = slv.scramble(20, 30)
            print("Scramble: {:s}", s)
            d = descramble(s)
            print("Descramble: {:s}", d)
            sleep(2)
