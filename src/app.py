#!/usr/bin/python3

import sys
import logging
import time
import yaml

from cubey import stepper
from cubey.scanner import Scanner
from cubey.solver import Solver
# from cubey.config import cfg


def main():
    """scan the cube, get a solution from kociemba, then execute it on the robot."""
    config_file = "config.yaml"
    config = {}
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    logging.basicConfig(
        level=logging.getLevelName(config['app']['logLevel']), format=config['app']['logFormat'])
    scanner = Scanner(config)
    solver = Solver(config)

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
