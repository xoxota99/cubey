"""
Motor controller for the Cubey robot
"""

import time
import logging
from typing import Dict, Any

from cubey.exceptions import MotorError

try:
    # Import GPIO library - this will fail if not on a Raspberry Pi
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO
    
# Constants for motor directions
CW = GPIO.LOW
CCW = GPIO.HIGH

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
        self.face_pins = config["motor"]["face_pins"]
        self.disable_pin = config["motor"]["disable_pin"]
        self.direction_pin = config["motor"]["direction_pin"]
        self.speed = config["motor"]["speed"]
        
        self.GPIO = GPIO
        self.GPIO.setmode(GPIO.BCM)
        self.GPIO.setwarnings(False)
        
        # Set up GPIO pins
        for pin in self.face_pins.values():
            self.GPIO.setup(pin, GPIO.OUT)
            self.GPIO.output(pin, GPIO.LOW)
        
        self.GPIO.setup(self.disable_pin, GPIO.OUT)
        self.GPIO.output(self.disable_pin, GPIO.LOW)

        self.GPIO.setup(self.direction_pin, GPIO.OUT)
        self.GPIO.output(self.direction_pin, CW)  #CW

        self.logger.info("Motor controller initialized")
            
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
        self.logger.debug(f"Executing: {recipe_str}")
        
        # Split the recipe into individual moves
        recipe = recipe_str.split()
        
        for move in recipe:
            if len(move) == 0:
                continue
                
            # Parse the move
            face = move[0]
            if face not in self.face_pins:
                raise MotorError(f"Invalid face: {face}")
                
            pin = self.face_pins[face]
            
            # Determine the direction and angle
            if len(move) > 1:
                if move[1] == "'":
                    self.rot_90(pin, CCW)
                elif move[1] == "2":
                    self.rot_180(pin)
                else:
                    raise MotorError(f"Invalid move modifier: {move[1]}")
            else:
                self.rot_90(pin, CW)
                
        return True
    
    def rot_90(self, motor_pin: int, direction: int = CW) -> None:
        """
        Rotate a face 90 degrees
        
        Args:
            motor_pin: GPIO pin for the motor
            direction: Direction to rotate (CW or CCW)
        """
        self.logger.debug(f"Rotating pin {motor_pin} 90 degrees, direction {direction}")
        
        if self.GPIO:
            #set direction
            self.GPIO.output(self.direction_pin,direction)
            
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
            #set direction
            self.GPIO.output(self.direction_pin,direction)
            
            self.GPIO.output(motor_pin, self.GPIO.HIGH)
            time.sleep(self.speed * 2 / 1000.0)
            self.GPIO.output(motor_pin, self.GPIO.LOW)
            
    def _stop(self) -> None:
        """
        Stop all motors and clean up GPIO
        """
        if self.GPIO:
            for pin in self.face_pins.values():
                self.GPIO.output(pin, self.GPIO.LOW)
                
            self.GPIO.cleanup()
            self.logger.debug("GPIO cleanup complete")
