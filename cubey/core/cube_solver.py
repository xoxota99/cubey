"""
Core cube solving functionality for Cubey
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple

import kociemba

from cubey.hardware.motorcontroller import MotorController
from cubey.solver.scanner import Scanner
from cubey.exceptions import SolverError

def solve_cube(config: Dict[str, Any], scanner: Scanner, motors: MotorController, 
               state: Optional[str] = None, interactive: bool = False) -> Tuple[int, Optional[str]]:
    """
    Solve the cube
    
    Args:
        config: Configuration dictionary
        scanner: Scanner instance
        motors: Motor controller instance
        state: Optional cube state string (if None, will scan the cube)
        interactive: Whether to run in interactive mode
        
    Returns:
        Tuple of (exit code, solution string)
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Scan the cube if no state provided
        if state is None:
            if interactive:
                input("Press any key to begin scanning the cube.")
                
            logger.info("Scanning cube...")
            t0 = round(time.time() * 1000)
            state = scanner.get_state_string(motors)
            t1 = round(time.time() * 1000)
            
            if state is None:
                logger.error("Failed to get a valid cube state. Please check the cube and try again.")
                return 1, None
                
            if interactive:
                logger.info(f"Scan complete! Cube state: {state}")
        else:
            logger.info(f"Using provided cube state: {state}")
            t0 = t1 = round(time.time() * 1000)
        
        # Solve the cube
        if interactive:
            input("Press any key to generate the solution.")
            
        logger.info("Solving cube...")
        t2 = round(time.time() * 1000)
        solution = kociemba.solve(state)
        t3 = round(time.time() * 1000)
        logger.info(f"Solution: {solution}")
        
        # Execute the solution
        if interactive:
            input("Press any key to execute the solution.")
            
        logger.info("Executing solution...")
        t4 = round(time.time() * 1000)
        motors.execute(solution)
        t5 = round(time.time() * 1000)
        
        # Log timing information
        logger.info(f'Scan time: {t1 - t0}ms')
        logger.info(f'Solve time: {t3 - t2}ms')
        logger.info(f'Execution time: {t5 - t4}ms')
        
        return 0, solution
    except Exception as e:
        logger.error(f"Error solving cube: {e}")
        return 1, None
