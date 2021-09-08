#!/usr/bin/python3

import sys
import logging
import time
import yaml

from cubey.stepper import MotorController
from cubey.scanner import Scanner
from cubey.solver import Solver


def solve(scanner, solver, motors):
    """scan the cube, get a solution from kociemba, then execute it on the robot."""
    logging.info("Scanning...")
    t0 = round(time.time() * 1000)
    state_str = scanner.get_state_string(motors)
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
    motors.execute(solution)
    t5 = round(time.time() * 1000)

    logging.info('Scan time: {:d}ms'.format(t1-t0))
    logging.info('Solve time: {:d}ms'.format(t3-t2))
    logging.info('Execution time: {:d}ms'.format(t5-t4))

    return(0)


def solve_interactive(scanner, solver, motors):
    """scan the cube, get a solution from kociemba, then execute it on the robot."""
    input("Press any key to begin scanning the cube.")
    t0 = round(time.time() * 1000)
    state_str = scanner.get_state_string(motors)
    t1 = round(time.time() * 1000)
    print("Scan complete! Cube state: {0}\n".format(state_str))

    input("Press any key to generate the solution.")

    t2 = round(time.time() * 1000)
    solution = solver.solve(state_str)
    t3 = round(time.time() * 1000)
    print("Finished solving! Solution: {0}\n".format(solution))

    input("Press any key to execute the solution.")

    t4 = round(time.time() * 1000)
    motors.execute(solution)
    t5 = round(time.time() * 1000)

    print('Scan time: {:d}ms'.format(t1-t0))
    print('Solve time: {:d}ms'.format(t3-t2))
    print('Execution time: {:d}ms'.format(t5-t4))

    return(0)


if __name__ == "__main__":
    config_file = "config.yaml"
    config = {}
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    logging.basicConfig(
        level=logging.getLevelName(config['app']['logLevel']), format=config['app']['logFormat'])
    scanner = Scanner(config)
    solver = Solver(config)
    motors = MotorController(config)

    solvers = {
        "DEFAULT": solve,
        "-I": solve_interactive
    }

    mode = "DEFAULT"

    if len(sys.argv) > 1:
        mode = sys.argv[1].upper()

    # non-interactive solver is the default, if not found.
    func = solvers.get(mode, solve)

    sys.exit(func(scanner, solver, motors))
