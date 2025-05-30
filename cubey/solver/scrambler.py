"""
Scrambler for the Cubey robot
"""

import random
import logging
from typing import Dict, Any, List, Optional

from cubey.exceptions import CubeyError

def generate_scramble(moves: int = 20) -> str:
    """
    Generate a random scramble sequence
    
    Args:
        moves: Number of moves in the scramble
        
    Returns:
        Scramble string
    """
    logger = logging.getLogger(__name__)
    logger.debug(f"Generating scramble with {moves} moves")
    
    recipe = ""
    base = "X"  # Placeholder
    last_base = "X"  # Placeholder

    for _ in range(moves):
        # Avoid repeating the same face
        while base == last_base:
            # Pick a random face
            base = random.choice(["U", "R", "F", "D", "L", "B"])

        last_base = base
        add = random.randint(0, 2)
        xtra = ""

        if add == 1:
            xtra = "'"
        elif add == 2:
            xtra = "2"

        recipe = recipe + base + xtra + " "

    logger.debug(f"Generated scramble: {recipe}")
    return recipe.strip()

def descramble(recipe_str: str) -> str:
    """
    Generate the inverse of a scramble sequence
    
    Args:
        recipe_str: Scramble string
        
    Returns:
        Inverse scramble string
    """
    logger = logging.getLogger(__name__)
    logger.debug(f"Generating inverse for scramble: {recipe_str}")
    
    recipe_arr = recipe_str.split()
    rec2 = ""
    
    for step in reversed(recipe_arr):
        if "'" in step:
            rec2 += step.replace("'", "") + " "
        elif "2" in step:
            rec2 += step + " "  # 180-degree turns are their own inverse
        else:
            rec2 += step + "' "

    logger.debug(f"Generated inverse: {rec2}")
    return rec2.strip()

class Scrambler:
    """
    Class for scrambling the cube
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the scrambler
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.min_moves = config.get("scrambler", {}).get("min_moves", 20)
        self.max_moves = config.get("scrambler", {}).get("max_moves", 25)
        
    def scramble(self, moves: Optional[int] = None) -> str:
        """
        Generate a random scramble
        
        Args:
            moves: Number of moves (if None, uses the configured range)
            
        Returns:
            Scramble string
        """
        if moves is None:
            moves = random.randint(self.min_moves, self.max_moves)
            
        return generate_scramble(moves)
