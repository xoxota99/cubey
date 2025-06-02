#!/usr/bin/env python3
"""
Command-line interface for Cubey
"""

import sys
import argparse
import logging
from typing import Optional, List

from cubey.config import get_merged_config
from cubey.utils.logging_config import setup_logging, get_logger
from cubey.utils.error_handler import handle_errors, setup_global_exception_handler
from cubey.ui.cli_controller import CLIController
from cubey.ui.web_controller import main as run_web_server

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
    solve_parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode"
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
    calibrate_parser = subparsers.add_parser("calibrate", help="Calibrate the scanner")
    calibrate_parser.add_argument(
        "--output",
        help="Output file for calibration data",
        default=None
    )
    
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
    
    # Create CLI controller
    controller = CLIController(config)
    
    # Execute command
    if parsed_args.command == "solve":
        return controller.solve(parsed_args.state, parsed_args.interactive)
    elif parsed_args.command == "scramble":
        return controller.scramble(parsed_args.moves)
    elif parsed_args.command == "scan":
        return controller.scan(parsed_args.output)
    elif parsed_args.command == "calibrate":
        from cubey.hardware.calibration import calibrate
        return calibrate(config, parsed_args.output)
    elif parsed_args.command == "manual":
        return controller.manual(parsed_args.moves)
    elif parsed_args.command == "web":
        run_web_server(
            host=parsed_args.host,
            port=parsed_args.port,
            config_path=parsed_args.config
        )
        return 0
    else:
        logger.error("No command specified. Use --help for usage information.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
