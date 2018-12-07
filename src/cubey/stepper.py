from time import sleep
import math
import pigpio
import yaml

# We are only spinning one motor at a time, so only need one DIR pin.
# (All motors are on the same DIR bus).
config_file = "config.yaml"
config = {}
with open(config_file, 'r') as ymlfile:
    config = yaml.load(ymlfile)

pins = config['stepper']['pins']
DIR = pins['dir']                # Direction GPIO Pin

UP = pins['up']                  # UP face stepper
RIGHT = pins['right']            # RIGHT face stepper
FRONT = pins['front']            # FRONT face stepper
DOWN = pins['down']              # DOWN face stepper
LEFT = pins['left']              # LEFT face stepper
BACK = pins['back']              # BACK face stepper
DISABLE = 0

if 'disable' in pins:
    DISABLE = pins['disable']

MOTOR_PIN = [UP, RIGHT, FRONT, DOWN, LEFT, BACK]  # Step GPIO Pins
FACE_NAME = ["U", "R", "F", "D", "L", "B"]
FACE_MOTOR_MAP = {
    "U": UP,
    "R": RIGHT,
    "F": FRONT,
    "D": DOWN,
    "L": LEFT,
    "B": BACK
}
RPM = config['stepper']['rpm']  # complete revolutions (360 deg.) per minute
# steps per revolution (varies by motor)
STEPS_PER_REVOLUTION = config['stepper']['steps_per_rev']
STEPS_PER_DEGREE = STEPS_PER_REVOLUTION / 360.0
STEP_FACTOR = config['stepper']['step_factor']
# PULSE_LENGTH_US = 1000000 // (STEPS_PER_REVOLUTION * RPM // 60)
# e.g. 4 revolutions per second = 800 steps per second.
# 800 steps per second = one step every 1250 uS.

MOVE_DELAY = config['stepper']['move_delay']

CW = 0
CCW = 1

HERTZ = config['stepper']['hertz']

pi = None       # pigpio reference
is_init = False


def _init(force=False):
    """
    _initialize stepper motor frequency / PWM ramps for 90 and 180-degree turns
    """
    global is_init, pi

    # Connect to pigpiod daemon
    pi = pigpio.pi()
    sleep(0.001)

    if force or not is_init:
        if DISABLE:
            pi.set_mode(DISABLE, pigpio.OUTPUT)
            pi.write(DISABLE, 1)

        # Set up pins as an output
        pi.set_mode(DIR, pigpio.OUTPUT)
        for i in MOTOR_PIN:
            pi.set_mode(i, pigpio.OUTPUT)

        is_init = True


def _stop():
    global is_init
    pi.stop()
    sleep(0.001)
    is_init = False


def _tx_pulses(pin, hertz, num, pulse_len=1):
    assert hertz < 500000
    length_us = int(1000000/hertz)
    assert int(pulse_len) < length_us
    assert num < 65536

    if DISABLE:
        pi.write(DISABLE, 0)
        sleep(0.001)       # one millisecond

    num_low = num % 256
    num_high = num // 256

    waveform = []

    waveform.append(pigpio.pulse(1 << pin, 0, pulse_len))
    waveform.append(pigpio.pulse(0, 1 << pin, length_us - pulse_len))

    pi.wave_add_generic(waveform)

    wid = pi.wave_create()

    if wid >= 0:
        pi.wave_chain([255, 0, wid, 255, 1, num_low, num_high])
        while pi.wave_tx_busy():
            pass
        pi.wave_delete(wid)

    if DISABLE:
        pi.write(DISABLE, 1)
        sleep(0.001)       # one millisecond


def rot_90(motor_pin, direction=CW):
    """
    rotate 90 degrees in the specified direction (CW or CCW)
    param:motor_pin - One of UP, RIGHT, FRONT, DOWN, LEFT, or BACK, as defined above.
    param:direction - One of CW or CCW, as defined above.
    """
    if not is_init:
        _init()
    pi.write(DIR, direction)
    _tx_pulses(motor_pin, HERTZ, int(90 * STEPS_PER_DEGREE * STEP_FACTOR))


def rot_180(motor_pin, direction=None):
    """
    rotate 180 degrees in the specified direction (CW or CCW)
    param:motor_pin - One of UP, RIGHT, FRONT, DOWN, LEFT, or BACK, as defined above.
    param:direction - One of CW or CCW, as defined above. Default is CW
    """
    if not is_init:
        _init()
    if direction is not None:
        pi.write(DIR, direction)
    _tx_pulses(motor_pin, HERTZ, int(180 * STEPS_PER_DEGREE * STEP_FACTOR))


def execute(recipe_str):
    """
    Take a recipe, of the form (e.g.) "R L2 F B U' F' D F' U B2 L' U2 B2 U D' B2 U2 L2 D' R2 D2"
    and execute it using the attached stepper motors.
    """
    if not is_init:
        _init()
    recipe = recipe_str.split()
    for step_str in recipe:
        base = step_str[0]
        # TODO: We can execut opposite side simultaneously, if the NEXT item in the list is OPPOSITE this item AND has the SAME orientation (CW or CCW) as this item.
        pin = FACE_MOTOR_MAP[base]
        if (len(step_str) >= 2):
            xtra = step_str[-1:]
            if (xtra == "'"):
                rot_90(pin, CCW)
            elif (xtra == "2"):
                rot_180(pin)
        else:
            rot_90(pin)
        sleep(MOVE_DELAY)
    _stop()
