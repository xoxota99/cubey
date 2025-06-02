"""
Motor controller for the Cubey robot
"""

import time
import logging
from typing import Dict, Any, List, Optional

from cubey.exceptions import MotorError

# Constants for motor directions
CW = 1
CCW = -1

class MotorController:
    """
    Controls the stepper motors that manipulate the cube
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the motor controller
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.motor_pins = config["motor"]["pins"]
        self.speed = config["motor"]["speed"]
        
        try:
            # Import GPIO library - this will fail if not on a Raspberry Pi
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.GPIO.setmode(GPIO.BCM)
            self.GPIO.setwarnings(False)
            
            # Set up GPIO pins
            for pin in self.motor_pins.values():
                self.GPIO.setup(pin, GPIO.OUT)
                self.GPIO.output(pin, GPIO.LOW)
                
            self.logger.info("Motor controller initialized")
        except ImportError:
            self.logger.warning("RPi.GPIO not available - running in simulation mode")
            self.GPIO = None
            
    def execute(self, recipe_str: str) -> bool:
        """
        Execute a sequence of cube moves
        
        Args:
            recipe_str: String of moves to execute (e.g., "F R U R' U' F'")
            
        Returns:
            True if successful
            
        Raises:
            MotorError: If an invalid move is encountered
        """
        Execute a sequence of cube moves
        
        Args:
            recipe_str: String of moves to execute (e.g., "F R U R' U' F'")
            
        Raises:
            MotorError: If an invalid move is encountered
        """
        if not recipe_str:
            return
            
        recipe_arr = recipe_str.split()
        
        for step in recipe_arr:
            self.logger.debug(f"Executing move: {step}")
            
            if len(step) == 0:
                continue
                
            base = step[0]
            
            if base not in self.motor_pins:
                raise MotorError(f"Invalid move: {step}")
                
            pin = self.motor_pins[base]
            
            if len(step) > 1:
                if step[1] == "'":
                    self.rot_90(pin, CCW)
                elif step[1] == "2":
                    self.rot_180(pin)
                else:
                    raise MotorError(f"Invalid move modifier: {step}")
            else:
                self.rot_90(pin, CW)
                
    def rot_90(self, motor_pin: int, direction: int = CW) -> None:
        """
        Rotate a face 90 degrees
        
        Args:
            motor_pin: GPIO pin for the motor
            direction: Direction to rotate (CW or CCW)
        """
        self.logger.debug(f"Rotating pin {motor_pin} 90 degrees, direction {direction}")
        
        if self.GPIO:
            self.GPIO.output(motor_pin, self.GPIO.HIGH)
            time.sleep(self.speed / 1000.0)
            self.GPIO.output(motor_pin, self.GPIO.LOW)
            
    def rot_180(self, motor_pin: int, direction: int = CW) -> None:
        """
        Rotate a face 180 degrees
        
        Args:
            motor_pin: GPIO pin for the motor
            direction: Direction to rotate (CW or CCW)
        """
        self.logger.debug(f"Rotating pin {motor_pin} 180 degrees")
        
        if self.GPIO:
            self.GPIO.output(motor_pin, self.GPIO.HIGH)
            time.sleep(self.speed * 2 / 1000.0)
            self.GPIO.output(motor_pin, self.GPIO.LOW)
            
    def _stop(self) -> None:
        """
        Stop all motors and clean up GPIO
        """
        if self.GPIO:
            for pin in self.motor_pins.values():
                self.GPIO.output(pin, self.GPIO.LOW)
                
            self.GPIO.cleanup()
            self.logger.debug("GPIO cleanup complete")
