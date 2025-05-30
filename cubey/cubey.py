import sys
import logging
import time
import yaml
import os

from lib.motorcontroller import MotorController
from lib.scanner import Scanner
from lib.logger import setup_logging
from config_validator import load_and_validate_config
import kociemba

"""
Main Cubey application
"""


def solve(scanner, motors):
    """scan the cube, get a solution from kociemba, then execute it on the robot."""
    logging.info("Scanning...")
    t0 = round(time.time() * 1000)
    state_str = scanner.get_state_string(motors)
    t1 = round(time.time() * 1000)
    
    if state_str is None:
        logging.error("Failed to get a valid cube state. Please check the cube and try again.")
        return 1
        
    logging.info("Scanned state: " + state_str)

    time.sleep(1)

    logging.info("Solving...")
    t2 = round(time.time() * 1000)
    solution = kociemba.solve(state_str)
    t3 = round(time.time() * 1000)
    logging.info("Solution: " + solution)

    logging.info("Executing...\n")
    t4 = round(time.time() * 1000)
    motors.execute(solution)
    t5 = round(time.time() * 1000)

    logging.info('Scan time: {:d}ms'.format(t1 - t0))
    logging.info('Solve time: {:d}ms'.format(t3 - t2))
    logging.info('Execution time: {:d}ms'.format(t5 - t4))

    return(0)


def solve_interactive(scanner, motors):
    """scan the cube, get a solution from kociemba, then execute it on the robot."""
    input("Press any key to begin scanning the cube.")
    t0 = round(time.time() * 1000)
    state_str = scanner.get_state_string(motors)
    t1 = round(time.time() * 1000)
    
    if state_str is None:
        logging.error("Failed to get a valid cube state. Please check the cube and try again.")
        return 1
        
    logging.info("Scan complete! Cube state: {0}\n".format(state_str))

    input("Press any key to generate the solution.")

    t2 = round(time.time() * 1000)
    solution = kociemba.solve(state_str)
    t3 = round(time.time() * 1000)
    logging.info("Finished solving! Solution: {0}\n".format(solution))

    input("Press any key to execute the solution.")

    t4 = round(time.time() * 1000)
    motors.execute(solution)
    t5 = round(time.time() * 1000)

    logging.info('Scan time: {:d}ms'.format(t1 - t0))
    logging.info('Solve time: {:d}ms'.format(t3 - t2))
    logging.info('Execution time: {:d}ms'.format(t5 - t4))

    return(0)


if __name__ == "__main__":
    # Use absolute path for configuration file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, "config.yaml")
    
    try:
        # Load and validate configuration
        config = load_and_validate_config(config_file)
        
        # Set up logging using the centralized logger
        setup_logging(config_file)
        logger = logging.getLogger(__name__)
        
        scanner = Scanner(config)
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
        
        sys.exit(func(scanner, motors))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
