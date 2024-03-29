from time import sleep
import pigpio

"""
Controller for stepper motors.
"""

config = {}
DIR_PIN = 0          # GPIO pin to set direction (cw / ccw)
DISABLE_PIN = 0      # GPIO pin to disable the stepper
FACE_MOTOR_MAP = {}  # map of faces to motor pins.

STEPS_PER_DEGREE = 200  # steps per degree (varies by motor)
STEP_FACTOR = 8  # number of pulses per step. (for microstepping)
MOVE_DELAY = 0.05  # take a small break beween stepper movements.
HERTZ = 400

CW = 1
CCW = 0

pi = None       # pigpio reference
is_init = False


class MotorController:

    def __init__(self, _config):
        global config, DIR_PIN, DISABLE_PIN, FACE_MOTOR_MAP, STEPS_PER_DEGREE, STEP_FACTOR, MOVE_DELAY, HERTZ

        config = _config

        pins = _config['stepper']['pin_map']

        # Direction GPIO Pin
        DIR_PIN = pins['dir']

        # Disable GPIO pin
        if 'disable' in pins:
            DISABLE_PIN = pins['disable']

        # map of faces to GPIO pins
        FACE_MOTOR_MAP = {
            "U": pins['up'],
            "R": pins['right'],
            "F": pins['front'],
            "D": pins['down'],
            "L": pins['left'],
            "B": pins['back']
        }

        # Number of stepper motor "steps" per degree of angle.
        STEPS_PER_DEGREE = config['stepper']['steps_per_rev'] / 360.0

        # micro-stepping factor.
        STEP_FACTOR = config['stepper']['step_factor']

        # seconds to wait between cube moves.
        MOVE_DELAY = config['stepper']['move_delay']

        HERTZ = config['stepper']['hertz']

    def _initialize(self, force=False):
        """
        _initialize stepper motor frequency / PWM ramps for 90 and 180-degree turns
        """
        global pi, is_init

        # Connect to pigpiod daemon
        pi = pigpio.pi()
        sleep(0.001)

        if force or not is_init:
            if DISABLE_PIN:
                pi.set_mode(DISABLE_PIN, pigpio.OUTPUT)
                pi.write(DISABLE_PIN, 1)

            # Set up pins as an output
            pi.set_mode(DIR_PIN, pigpio.OUTPUT)
            for _, val in config['stepper']['pin_map'].items():
                pi.set_mode(val, pigpio.OUTPUT)

            is_init = True

    def _stop(self):
        global is_init
        if is_init:
            pi.stop()
            sleep(0.001)
            is_init = False

    def _tx_pulses(self, pin, hertz, num):
        assert hertz < 500000

        # length of shortest possible pulse, in microseconds.
        length_us = int(1000000 / hertz)

        assert num < 65536

        if DISABLE_PIN:
            pi.write(DISABLE_PIN, 0)
            sleep(0.001)       # one millisecond

        num_low = num % 256
        num_high = num // 256

        waveform = []

        waveform.append(pigpio.pulse(gpio_on=1 << pin,
                        gpio_off=0, delay=1))    # rising edge
        waveform.append(pigpio.pulse(
            gpio_on=0, gpio_off=1 << pin, delay=length_us - 1))     # falling edge

        pi.wave_add_generic(waveform)

        wid = pi.wave_create()

        if wid >= 0:
            pi.wave_chain([255, 0, wid, 255, 1, num_low, num_high])
            while pi.wave_tx_busy():
                pass
            pi.wave_delete(wid)

        if DISABLE_PIN:
            pi.write(DISABLE_PIN, 1)
            sleep(0.001)       # one millisecond

    def rot_90(self, motor_pin, direction=CW):
        """
        rotate 90 degrees in the specified direction (CW or CCW)
        param:motor_pin - One of UP, RIGHT, FRONT, DOWN, LEFT, or BACK, as defined above.
        param:direction - One of CW or CCW, as defined above.
        """
        if not is_init:
            self._initialize()
        pi.write(DIR_PIN, direction)
        steps = int(90 * STEPS_PER_DEGREE * STEP_FACTOR)

        self._tx_pulses(motor_pin, HERTZ, steps)

    def rot_180(self, motor_pin):
        """
        rotate 180 degrees in the specified direction (CW or CCW)
        param:motor_pin - One of UP, RIGHT, FRONT, DOWN, LEFT, or BACK, as defined above.
        param:direction - One of CW or CCW, as defined above. Default is CW
        """
        if not is_init:
            self._initialize()
        pi.write(DIR_PIN, CW)
        steps = int(180 * STEPS_PER_DEGREE * STEP_FACTOR)

        self._tx_pulses(motor_pin, HERTZ, steps)

    def execute(self, recipe_str):
        """
        Take a recipe, of the form (e.g.) "R L2 F B U' F' D F' U B2 L' U2 B2 U D' B2 U2 L2 D' R2 D2"
        and execute it using the attached stepper motors.
        """

        if not is_init:
            self._initialize()
        recipe = recipe_str.split()
        for step_str in recipe:
            base = step_str[0]
            # TODO: We can execute opposite sides simultaneously, if the NEXT item in the list is OPPOSITE this item AND has the SAME orientation (CW or CCW) as this item.
            pin = FACE_MOTOR_MAP[base]
            if (len(step_str) >= 2):
                xtra = step_str[-1:]
                if (xtra == "'"):
                    self.rot_90(pin, CCW)
                elif (xtra == "2"):
                    self.rot_180(pin)
            else:
                self.rot_90(pin)
            sleep(MOVE_DELAY)
        self._stop()
