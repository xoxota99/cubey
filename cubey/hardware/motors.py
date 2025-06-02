"""
Motors module for the Cubey robot
"""

import logging
from cmd import Cmd
from typing import Dict, Any

from cubey.hardware.motorcontroller import MotorController

class MotorPrompt(Cmd):
    """
    Interactive command prompt for controlling the motors
    
    Allows the user to enter Rubik's Cube notation commands to control the motors
    """

    def __init__(self, motors: MotorController):
        """
        Initialize the motor prompt
        
        Args:
            motors: Motor controller instance
        """
        self.motors = motors
        super(MotorPrompt, self).__init__()

    def default(self, inp: str) -> bool:
        """
        Handle default input (cube notation)
        
        Args:
            inp: Input string
            
        Returns:
            True if the command should exit, False otherwise
        """
        if inp == "Q" or inp == "EOF":
            return self.do_q(inp)

        self.motors.execute(inp.upper())
        return False

    def emptyline(self) -> None:
        """
        Handle empty line input
        """
        # do nothing.
        pass

    def do_q(self, inp: str) -> bool:
        """
        Handle quit command
        
        Args:
            inp: Input string
            
        Returns:
            True to exit the command loop
        """
        print("Bye")
        return True

def run_interactive_mode(config: Dict[str, Any]) -> int:
    """
    Run the motors in interactive mode
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Exit code
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting interactive motor control")
    
    try:
        motors = MotorController(config)
        
        print("""
        Utility for interactively commanding the Stepper motors of the robot, using typical Rubik's Cube notation:
        R - Turn RIGHT face clockwise 90 degrees
        R2 - Turn RIGHT face 180 degrees (in an undefined direction)
        R' - Turn RIGHT face counter-clockwise 90 degrees.

        For "R" above, you can substitute any of:
        F - FRONT face
        U - UP face
        L - LEFT face
        B - BACK face
        D - DOWN face

        You can chain together commands in a single line, such as: D2 R2 U L' B' D R L' B U2 F L2 U2 L2 U' F2 D' B2 U' B2 U2 
        
        """)

        prompt = MotorPrompt(motors)
        prompt.prompt = "Cubey > "
        prompt.cmdloop()
        
        # Ensure motors are stopped
        motors._stop()
        
        return 0
    except Exception as e:
        logger.error(f"Error in interactive motor control: {e}")
        return 1
