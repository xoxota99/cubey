from time import sleep
import pigpio
import logging
from lib.logger import setup_logging
from typing import Dict, Optional, Union, List, Tuple, Any

"""
Controller for stepper motors.
"""

class MotorController:
    """
    Controller for stepper motors that manipulate the Rubik's Cube.
    
    This class provides methods to control the stepper motors that rotate the faces
    of the Rubik's Cube. It uses the pigpio library to control the GPIO pins on the
    Raspberry Pi.
    """
    
    # Class constants
    CW = 1  # Clockwise direction
    CCW = 0  # Counter-clockwise direction
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the MotorController with the given configuration.
        
        Args:
            config: Dictionary containing configuration parameters
        """
        self.__config = config
        self.__pi = None
        self.__is_init = False
        
        pins = config['stepper']['pin_map']
        
        # Direction GPIO Pin
        self.__dir_pin = pins['dir']
        
        # Disable GPIO pin
        self.__disable_pin = pins.get('disable', 0)
        
        # Map of faces to GPIO pins
        self.__face_motor_map = {
            "U": pins['up'],
            "R": pins['right'],
            "F": pins['front'],
            "D": pins['down'],
            "L": pins['left'],
            "B": pins['back']
        }
        
        # Number of stepper motor "steps" per degree of angle
        self.__steps_per_degree = config['stepper']['steps_per_rev'] / 360.0
        
        # Micro-stepping factor
        self.__step_factor = config['stepper']['step_factor']
        
        # Seconds to wait between cube moves
        self.__move_delay = config['stepper']['move_delay']
        
        # Pulses per second (speed)
        self.__hertz = config['stepper']['hertz']

    def _initialize(self, force: bool = False) -> None:
        """
        Initialize stepper motor frequency / PWM ramps for 90 and 180-degree turns.
        
        Args:
            force: If True, reinitialize even if already initialized
        
        Raises:
            Exception: If initialization fails
        """
        try:
            # Connect to pigpiod daemon
            self.__pi = pigpio.pi()
            sleep(0.001)
            
            if force or not self.__is_init:
                if self.__disable_pin:
                    self.__pi.set_mode(self.__disable_pin, pigpio.OUTPUT)
                    self.__pi.write(self.__disable_pin, 1)
                
                # Set up pins as outputs
                self.__pi.set_mode(self.__dir_pin, pigpio.OUTPUT)
                for _, val in self.__config['stepper']['pin_map'].items():
                    self.__pi.set_mode(val, pigpio.OUTPUT)
                
                self.__is_init = True
        except Exception as e:
            logging.error(f"Failed to initialize motor controller: {e}")
            self._stop()
            raise
    
    def _stop(self) -> None:
        """Stop the motor controller and release resources."""
        if self.__is_init and self.__pi is not None:
            self.__pi.stop()
            sleep(0.001)
            self.__is_init = False
    
    def _tx_pulses(self, pin: int, hertz: int, num: int) -> None:
        """
        Transmit pulses to the stepper motor.
        
        Args:
            pin: GPIO pin to pulse
            hertz: Frequency of pulses
            num: Number of pulses to send
        
        Raises:
            AssertionError: If hertz is too high or num is too large
        """
        assert hertz < 500000, "Hertz value too high"
        assert num < 65536, "Number of pulses too large"
        
        # Length of shortest possible pulse, in microseconds
        length_us = int(1000000 / hertz)
        
        if self.__disable_pin:
            self.__pi.write(self.__disable_pin, 0)
            sleep(0.001)  # One millisecond
        
        num_low = num % 256
        num_high = num // 256
        
        waveform = []
        
        # Rising edge
        waveform.append(pigpio.pulse(gpio_on=1 << pin, gpio_off=0, delay=1))
        # Falling edge
        waveform.append(pigpio.pulse(gpio_on=0, gpio_off=1 << pin, delay=length_us - 1))
        
        self.__pi.wave_add_generic(waveform)
        
        wid = self.__pi.wave_create()
        
        if wid >= 0:
            self.__pi.wave_chain([255, 0, wid, 255, 1, num_low, num_high])
            while self.__pi.wave_tx_busy():
                pass
            self.__pi.wave_delete(wid)
        
        if self.__disable_pin:
            self.__pi.write(self.__disable_pin, 1)
            sleep(0.001)  # One millisecond

    def rot_90(self, motor_pin: int, direction: int = CW) -> None:
        """
        Rotate 90 degrees in the specified direction.
        
        Args:
            motor_pin: GPIO pin for the motor to rotate
            direction: Direction to rotate (CW or CCW)
        """
        if not self.__is_init:
            self._initialize()
        
        self.__pi.write(self.__dir_pin, direction)
        steps = int(90 * self.__steps_per_degree * self.__step_factor)
        
        self._tx_pulses(motor_pin, self.__hertz, steps)
    
    def rot_180(self, motor_pin: int, direction: int = CW) -> None:
        """
        Rotate 180 degrees in the specified direction.
        
        Args:
            motor_pin: GPIO pin for the motor to rotate
            direction: Direction to rotate (CW or CCW)
        """
        if not self.__is_init:
            self._initialize()
        
        self.__pi.write(self.__dir_pin, direction)
        steps = int(180 * self.__steps_per_degree * self.__step_factor)
        
        self._tx_pulses(motor_pin, self.__hertz, steps)
    
    def execute(self, recipe_str: str) -> bool:
        """
        Take a recipe in cube notation and execute it using the attached stepper motors.
        
        Args:
            recipe_str: String containing cube notation moves to execute
            
        Returns:
            bool: True if execution was successful, False otherwise
            
        Raises:
            ValueError: If the recipe contains invalid cube notation
        """
        if not recipe_str or not isinstance(recipe_str, str):
            logging.error(f"Invalid recipe: {recipe_str}")
            return False

        if not self.__is_init:
            self._initialize()
            
        recipe = recipe_str.split()
        valid_faces = set(self.__face_motor_map.keys())
        valid_modifiers = set(['', '\'', '2'])
        
        # Validate the recipe before executing
        for step_str in recipe:
            if not step_str or len(step_str) > 2:
                logging.error(f"Invalid move in recipe: {step_str}")
                return False
                
            base = step_str[0]
            modifier = step_str[1:] if len(step_str) > 1 else ''
            
            if base not in valid_faces:
                logging.error(f"Invalid face in recipe: {base}")
                return False
                
            if modifier not in valid_modifiers:
                logging.error(f"Invalid modifier in recipe: {modifier}")
                return False
        
        # Execute the validated recipe
        for step_str in recipe:
            base = step_str[0]
            # TODO: We can execute opposite sides simultaneously, if the NEXT item in the list is OPPOSITE this item AND has the SAME orientation (CW or CCW) as this item.
            pin = self.__face_motor_map[base]
            if (len(step_str) >= 2):
                xtra = step_str[-1:]
                if (xtra == "'"):
                    self.rot_90(pin, self.CCW)
                elif (xtra == "2"):
                    self.rot_180(pin)
            else:
                self.rot_90(pin)
            sleep(self.__move_delay)
        self._stop()
        return True
