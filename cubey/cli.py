#!/usr/bin/env python3
"""
Command-line interface for Cubey
"""

import os
import sys
import argparse
import logging
from typing import Optional, List, Dict, Any

from cubey.utils.config import get_merged_config
from cubey.utils.logging_config import setup_logging, get_logger
from cubey.utils.error_handler import handle_errors, setup_global_exception_handler
from cubey.exceptions import CubeyError

logger = get_logger(__name__)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Cubey - A Raspberry Pi-based Rubik's Cube solving robot",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--config",
        help="Path to configuration file",
        default=None
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Solve command
    solve_parser = subparsers.add_parser("solve", help="Solve the cube")
    solve_parser.add_argument(
        "--state",
        help="Cube state string (if not provided, will scan the cube)",
        default=None
    )
    
    # Scramble command
    scramble_parser = subparsers.add_parser("scramble", help="Scramble the cube")
    scramble_parser.add_argument(
        "--moves",
        type=int,
        default=20,
        help="Number of moves for scrambling"
    )
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan the cube")
    scan_parser.add_argument(
        "--output",
        help="Output file for the scanned state",
        default=None
    )
    
    # Calibrate command
    subparsers.add_parser("calibrate", help="Calibrate the scanner")
    
    # Manual command
    manual_parser = subparsers.add_parser("manual", help="Manual control")
    manual_parser.add_argument(
        "moves",
        nargs="?",
        help="Moves to execute (e.g., 'F R U R\\' U\\' F\\')",
        default=None
    )
    
    # Web command
    web_parser = subparsers.add_parser("web", help="Start the web interface")
    web_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the web server to"
    )
    web_parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind the web server to"
    )
    
    return parser.parse_args(args)


@handle_errors(exit_on_error=True)
def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the command-line interface
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code
    """
    # Parse arguments
    parsed_args = parse_args(args)
    
    # Set up logging
    setup_logging()
    logging.getLogger().setLevel(getattr(logging, parsed_args.log_level))
    
    # Set up global exception handler
    setup_global_exception_handler()
    
    # Load configuration
    config = get_merged_config(parsed_args.config)
    
    # Execute command
    if parsed_args.command == "solve":
        from cubey.core.scanner import Scanner
        from cubey.core.motorcontroller import MotorController
        import cubey
        
        motors = MotorController(config)
        scanner = Scanner(config)
        
        if parsed_args.state:
            state = parsed_args.state
        else:
            logger.info("Scanning cube...")
            state = scanner.get_state_string(motors)
            
        if not state:
            logger.error("Failed to get cube state")
            return 1
            
        logger.info(f"Cube state: {state}")
        logger.info("Solving...")
        solution = cubey.kociemba.solve(state)
        logger.info(f"Solution: {solution}")
        
        logger.info("Executing solution...")
        motors.execute(solution)
        logger.info("Done!")
        
    elif parsed_args.command == "scramble":
        from cubey.core.motorcontroller import MotorController
        from cubey.scramble import generate_scramble
        
        motors = MotorController(config)
        
        scramble = generate_scramble(parsed_args.moves)
        logger.info(f"Scramble: {scramble}")
        
        logger.info("Executing scramble...")
        motors.execute(scramble)
        logger.info("Done!")
        
    elif parsed_args.command == "scan":
        from cubey.core.scanner import Scanner
        from cubey.core.motorcontroller import MotorController
        
        motors = MotorController(config)
        scanner = Scanner(config)
        
        logger.info("Scanning cube...")
        state = scanner.get_state_string(motors)
        
        if not state:
            logger.error("Failed to get cube state")
            return 1
            
        logger.info(f"Cube state: {state}")
        
        if parsed_args.output:
            with open(parsed_args.output, "w") as f:
                f.write(state)
            logger.info(f"State written to {parsed_args.output}")
            
    elif parsed_args.command == "calibrate":
        from cubey.calibrate import calibrate
        
        logger.info("Starting calibration...")
        calibrate(config)
        
    elif parsed_args.command == "manual":
        from cubey.core.motorcontroller import MotorController
        
        motors = MotorController(config)
        
        if parsed_args.moves:
            logger.info(f"Executing moves: {parsed_args.moves}")
            motors.execute(parsed_args.moves)
            logger.info("Done!")
        else:
            logger.info("Enter moves (e.g., 'F R U R\\' U\\' F\\'). Type 'quit' to exit.")
            while True:
                try:
                    moves = input("> ")
                    if moves.lower() in ("quit", "exit", "q"):
                        break
                    motors.execute(moves)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    
    elif parsed_args.command == "web":
        from cubey.web.app import main as run_web_server
        
        logger.info(f"Starting web server on {parsed_args.host}:{parsed_args.port}...")
        run_web_server(host=parsed_args.host, port=parsed_args.port, config_path=parsed_args.config)
        
    else:
        logger.error("No command specified. Use --help for usage information.")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
