"""
Kociemba solver for the Cubey robot
"""

import logging
import time
from typing import Dict, Any, List, Optional

import kociemba

from cubey.exceptions import SolverError

class KociembaSolver:
    """
    Solver using Herbert Kociemba's two-phase algorithm
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the solver
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
    def solve(self, state: str) -> str:
        """
        Solve the cube using Kociemba's algorithm
        
        Args:
            state: String representation of the cube state
            
        Returns:
            Solution string
            
        Raises:
            SolverError: If the cube state is invalid or the solver fails
        """
        self.logger.info(f"Solving cube with state: {state}")
        
        try:
            start_time = time.time()
            solution = kociemba.solve(state)
            end_time = time.time()
            
            self.logger.info(f"Solution found in {end_time - start_time:.3f} seconds: {solution}")
            return solution
        except Exception as e:
            self.logger.error(f"Error solving cube: {e}")
            raise SolverError(f"Failed to solve cube: {e}")
            
    def validate_state(self, state: str) -> bool:
        """
        Validate a cube state
        
        Args:
            state: String representation of the cube state
            
        Returns:
            True if the state is valid, False otherwise
        """
        if not state or len(state) != 54:
            self.logger.error(f"Invalid state length: {len(state) if state else 0}, expected 54")
            return False
            
        # Check if the state contains only valid colors
        valid_colors = set("URFDLB")
        if not all(c in valid_colors for c in state):
            self.logger.error(f"Invalid colors in state: {set(state) - valid_colors}")
            return False
            
        # Check if the state has the correct number of each color
        for color in valid_colors:
            if state.count(color) != 9:
                self.logger.error(f"Invalid color count for {color}: {state.count(color)}, expected 9")
                return False
                
        return True
