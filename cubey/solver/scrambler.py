"""
Scrambler module for the Cubey robot
"""

import logging
import random
from typing import Dict, Any, Optional

from cubey.hardware.motorcontroller import MotorController

def generate_scramble(min_moves: int, max_moves: int) -> str:
    """
    Generate a random scramble sequence
    
    Args:
        min_moves: Minimum number of moves
        max_moves: Maximum number of moves
        
    Returns:
        Scramble sequence as a string
    """
    recipe = ""
    move_count = random.randint(min_moves, max_moves)
    base = "X"
    last_base = "X"

    for _ in range(move_count):
        while base == last_base:
            # pick a random face
            base = random.choice(["U", "R", "F", "D", "L", "B"])

        last_base = base
        add = random.randint(0, 4)
        xtra = ""

        if add == 1:
            xtra = "'"
        elif add == 2:
            xtra = "2"

        recipe = recipe + base + xtra + " "

    return recipe.strip()

def generate_descramble(scramble: str) -> str:
    """
    Generate a descramble sequence from a scramble sequence
    
    Args:
        scramble: Scramble sequence
        
    Returns:
        Descramble sequence as a string
    """
    recipe_arr = scramble.split()
    rec2 = ""
    for step in reversed(recipe_arr):
        if("'" in step):
            rec2 += step.replace("'", "") + " "
        elif ("2" not in step):
            rec2 += step + "' "
        else:
            rec2 += step + " "

    return rec2.strip()

def scramble_cube(config: Dict[str, Any], motors: MotorController, moves: Optional[int] = None) -> str:
    """
    Scramble the cube
    
    Args:
        config: Configuration dictionary
        motors: Motor controller
        moves: Optional number of moves (if None, uses config values)
        
    Returns:
        Scramble sequence
    """
    logger = logging.getLogger(__name__)
    
    # Get scramble parameters from config
    min_moves = config.get("scrambler", {}).get("min_moves", 20)
    max_moves = config.get("scrambler", {}).get("max_moves", 30)
    
    # Override with provided moves if specified
    if moves is not None:
        min_moves = max_moves = moves
    
    # Generate and execute scramble
    scramble = generate_scramble(min_moves, max_moves)
    logger.info(f"Scrambling cube with sequence: {scramble}")
    motors.execute(scramble)
    
    return scramble

def descramble_cube(motors: MotorController, scramble: str) -> str:
    """
    Descramble the cube
    
    Args:
        motors: Motor controller
        scramble: Scramble sequence
        
    Returns:
        Descramble sequence
    """
    logger = logging.getLogger(__name__)
    
    # Generate and execute descramble
    descramble = generate_descramble(scramble)
    logger.info(f"Descrambling cube with sequence: {descramble}")
    motors.execute(descramble)
    
    return descramble
