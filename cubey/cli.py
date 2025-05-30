#!/usr/bin/env python3
import argparse
import sys
import os
import logging
import yaml

from lib.logger import setup_logging
from config_validator import load_and_validate_config
from lib.motorcontroller import MotorController
from lib.scanner import Scanner
import cubey

"""
Command-line interface for the cubey project
"""

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Cubey - A Raspberry Pi-based Rubik's Cube solving robot",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Solve command
    solve_parser = subparsers.add_parser("solve", help="Solve the cube")
    solve_parser.add_argument(
        "-i", "--interactive", 
        action="store_true", 
        help="Run in interactive mode"
    )
    
    # Scramble command
    scramble_parser = subparsers.add_parser("scramble", help="Scramble the cube")
    scramble_parser.add_argument(
        "-m", "--min-moves", 
        type=int, 
        default=20, 
        help="Minimum number of scramble moves"
    )
    scramble_parser.add_argument(
        "-M", "--max-moves", 
        type=int, 
        default=30, 
        help="Maximum number of scramble moves"
    )
    
    # Calibrate command
    calibrate_parser = subparsers.add_parser("calibrate", help="Calibrate the cube scanner")
    calibrate_parser.add_argument(
        "-o", "--output", 
        type=str, 
        help="Output file for calibration data"
    )
    
    # Manual control command
    manual_parser = subparsers.add_parser("manual", help="Manually control the cube")
    
    # Common arguments
    parser.add_argument(
        "-c", "--config", 
        type=str, 
        default="config.yaml", 
        help="Path to configuration file"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the CLI"""
    args = parse_args()
    
    # Determine the configuration file path
    if os.path.isabs(args.config):
        config_file = args.config
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(script_dir, args.config)
    
    try:
        # Load and validate configuration
        config = load_and_validate_config(config_file)
        
        # Set up logging
        log_level = "DEBUG" if args.verbose else config['app']['log_level']
        config['app']['log_level'] = log_level
        setup_logging(config_file)
        logger = logging.getLogger(__name__)
        
        # Initialize components
        scanner = Scanner(config)
        motors = MotorController(config)
        
        # Execute the requested command
        if args.command == "solve":
            if args.interactive:
                return cubey.solve_interactive(scanner, motors)
            else:
                return cubey.solve(scanner, motors)
        elif args.command == "scramble":
            import scramble
            recipe = scramble.scramble(args.min_moves, args.max_moves)
            logger.info(f"Scramble recipe: {recipe}")
            motors.execute(recipe)
            return 0
        elif args.command == "calibrate":
            import calibrate
            calib_data = calibrate.calibrate(motors)
            if args.output:
                with open(args.output, "w") as outfile:
                    yaml.dump(calib_data, outfile, default_flow_style=True)
                logger.info(f"Calibration data saved to {args.output}")
            else:
                logger.info(yaml.dump(calib_data, default_flow_style=True))
            return 0
        elif args.command == "manual":
            import motors as motors_module
            p = motors_module.MyPrompt(motors)
            p.prompt = "Cubey > "
            p.cmdloop()
            return 0
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
