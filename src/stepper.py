from __future__ import division
from time import sleep
import math
import pigpio
from config import cfg

# We are only spinning one motor at a time, so only need one DIR pin.
# (All motors are on the same DIR bus).
pins = cfg['stepper']['pins']
DIR = pins['dir']                # Direction GPIO Pin

UP = pins['up']                  # UP face stepper
RIGHT = pins['right']            # RIGHT face stepper
FRONT = pins['front']            # FRONT face stepper
DOWN = pins['down']              # DOWN face stepper
LEFT = pins['left']              # LEFT face stepper
BACK = pins['back']              # BACK face stepper

MOTOR_PIN = [UP, RIGHT, FRONT, DOWN, LEFT, BACK]  # Step GPIO Pins
STEP_NAME = ["U", "R", "F", "D", "L", "B"]
STEP_MAP = {
    "U": UP,
    "D": DOWN,
    "F": FRONT,
    "B": BACK,
    "L": LEFT,
    "R": RIGHT
}
RPM = cfg['stepper']['rpm']  # complete revolutions (360 deg.) per minute
# steps per revolution (varies by motor)
STEPS_PER_REVOLUTION = cfg['stepper']['steps_per_rev']
STEPS_PER_DEGREE = STEPS_PER_REVOLUTION / 360.0
STEP_FACTOR = cfg['stepper']['step_factor']
PULSE_LENGTH_US = 1000000 // (STEPS_PER_REVOLUTION * RPM // 60)
# e.g. 4 revolutions per second = 800 steps per second.
# 800 steps per second = one step every 1250 uS.

MOVE_DELAY = cfg['stepper']['move_delay']

CW = 1
CCW = 0

ramp_90 = []
ramp_180 = []


# Connect to pigpiod daemon
pi = pigpio.pi()

HERTZ = cfg['stepper']['hertz']
# allowed frequencies for pigpio sample rate 5 (the default)
ALLOWED_FREQS = [
    10, 20, 40, 50, 80, 100, 160, 200, 250, 320, 400
    # , 500, 800, 1000, 1600, 2000, 4000, 8000
]
is_init = False


def init(force=False):
    """
    Initialize stepper motor frequency / PWM ramps for 90 and 180-degree turns
    """
    global ramp_90, ramp_180, is_init

    if force or not is_init:
        # Set up pins as an output
        pi.set_mode(DIR, pigpio.OUTPUT)
        for i in MOTOR_PIN:
            pi.set_mode(i, pigpio.OUTPUT)

        is_init = True


def tx_pulses(pin, hertz, num, pulse_len=1):
    assert hertz < 500000
    length_us = int(1000000/hertz)
    assert int(pulse_len) < length_us
    assert num < 65536

    num_low = num % 256
    num_high = num // 256

    wf = []

    wf.append(pigpio.pulse(1 << pin, 0, pulse_len))
    wf.append(pigpio.pulse(0, 1 << pin, length_us - pulse_len))

    pi.wave_add_generic(wf)

    wid = pi.wave_create()

    if wid >= 0:
        pi.wave_chain([255, 0, wid, 255, 1, num_low, num_high])
        while pi.wave_tx_busy():
            sleep(0.01)
        pi.wave_delete(wid)


def rot_90(motor_pin, direction=CW):
    """
    rotate 90 degrees in the specified direction (CW or CCW)
    param:motor_pin - One of UP, RIGHT, FRONT, DOWN, LEFT, or BACK, as defined above.
    param:direction - One of CW or CCW, as defined above.
    """
    if not is_init:
        init()
    pi.write(DIR, direction)
    tx_pulses(motor_pin, HERTZ, int(90 * STEPS_PER_DEGREE * STEP_FACTOR))


def rot_180(motor_pin, direction=CW):
    """
    rotate 180 degrees in the specified direction (CW or CCW)
    param:motor_pin - One of UP, RIGHT, FRONT, DOWN, LEFT, or BACK, as defined above.
    param:direction - One of CW or CCW, as defined above. Default is CW
    """
    if not is_init:
        init()
    pi.write(DIR, direction)
    tx_pulses(motor_pin, HERTZ, int(180 * STEPS_PER_DEGREE * STEP_FACTOR))


def execute(recipe_str):
    """
    Take a recipe, of the form (e.g.) "R L2 F B U' F' D F' U B2 L' U2 B2 U D' B2 U2 L2 D' R2 D2"
    and execute it using the attached stepper motors.
    """
    recipe = recipe_str.split()
    for step_str in recipe:
        base = step_str[0]
        pin = STEP_MAP[base]
        if (len(step_str) >= 2):
            xtra = step_str[-1:]
            if (xtra == "'"):
                rot_90(pin, CCW)
            elif (xtra == "2"):
                rot_180(pin)
        else:
            rot_90(pin)
        sleep(MOVE_DELAY)


if __name__ == "__main__":
    init()
    print("Stepper test.")
    delay = MOVE_DELAY

    # rotate each side 90 degrees, four times, with a pause between each rotation.
    for s, mot in zip(STEP_NAME, MOTOR_PIN):
        # s = "U"
        mot = STEP_MAP[s]
        for _ in range(4):
            print(s)
            rot_90(mot, CW)
            sleep(delay)
        for _ in range(4):
            print(s+"'")
            rot_90(mot, CCW)
            sleep(delay)

    # rotate each side twice, 180 degrees, with a pause between each rotation.
    for s, mot in zip(STEP_NAME, MOTOR_PIN):
        for _ in range(2):
            print("2" + s)
            rot_180(mot, CW)
            sleep(delay)
        for _ in range(2):
            print("2"+s+"'")
            rot_180(mot, CCW)
            sleep(delay)
