from time import sleep
from __future__ import division
import math
import pigpio

# We are only spinning one motor at a time, so only need one DIR pin.
# (All motors are on the same DIR bus).
DIR = 17                # Direction GPIO Pin

UP = 18
RIGHT = 3
FRONT = 14
DOWN = 5
LEFT = 4
BACK = 2

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
RPM = 60  # complete revolutions (360 deg.) per minute
STEPS_PER_REVOLUTION = 200  # steps per revolution (varies by motor)
STEPS_PER_DEGREE = 360.0 / STEPS_PER_REVOLUTION
PULSE_LENGTH_US = 1000000 // (STEPS_PER_REVOLUTION * RPM // 60)
# e.g. 4 revolutions per second = 800 steps per second.
# 800 steps per second = one step every 1250 uS.

CW = 1
CCW = 0


ramp_90 = []
ramp_180 = []


# Connect to pigpiod daemon
pi = pigpio.pi()

# allowed frequencies for pigpio sample rate 5 (the default)
ALLOWED_FREQS = [
    10, 20, 40, 50, 80, 100, 160, 200, 250, 320, 400
    # , 500, 800, 1000, 1600, 2000, 4000, 8000
]
is_init = False

# initialize a frequency ramp for a turn of the specified number of degrees (typically 90 or 180 for our case).
# A frequency ramp is basically a list, with each element a pair of integers, [Frequency, Steps]. This ramp
# acts like a set of instructions to pigpiod, "Cycle the specified GPIO pin this many steps, at this frequency,
# then move on to the next item in the list."


def init_ramp(degrees):
    retval = []  # the ramp to return.
    deg = 0  # the last absolue angle that we saw
    lastfreq = 0  # the last frequency we saw in the loop.
    lastfreq_count = 1  # the count of the last frequency we saw in the loop.

    SLOPE_MAX = math.pi  # maximum slope of the acceleration curve.
    # accumulator, to double-check we are generating exactly the right number of steps.
    stepcheck = 0
    # number of steps we should generate.
    steps = int(STEPS_PER_DEGREE * degrees)
    halfdeg = degrees // 2  # half the arc.

    for i in range(steps):  # for each step we need
        # what angle do we think we're at? (from 0 to degrees)
        deg2 = halfdeg - math.cos(i / steps * math.pi) * halfdeg

        # what was the last angle? Check the slope against our maximum slope.
        slope = (deg2 - deg) / SLOPE_MAX

        # keep track of the current angle for next loop.
        deg = deg2

        # figure out our frequency, from the list of allowed frequencies for pigpiod sample rate.
        freq = ALLOWED_FREQS[int(slope * len(ALLOWED_FREQS))]
        # if this is the same frequency as the last iteration.
        if (lastfreq == freq):
            lastfreq_count += 1  # accumulate it.
        else:  # otherwise
            # add the last iteration to the ramp, with the last count.
            retval.append([lastfreq, lastfreq_count])
            # accumulate the count of steps so far.
            stepcheck += lastfreq_count
            lastfreq = freq  # re-initialize the tracking frequency
            lastfreq_count = 1  # and count.

    # escaped the loop. Add the last accumulated frequency to the ramp.
    retval.append([lastfreq, lastfreq_count])
    stepcheck += lastfreq_count

    # assert that we have, in fact, accumulated the target number of steps, and that we will therefore turn the exact correct number of degrees.
    assert stepcheck == steps

    # return the ramp.
    return retval


def init(force=False):
    global ramp_90, ramp_180, is_init

    if force or not is_init:
        # Set up pins as an output
        pi.set_mode(DIR, pigpio.OUTPUT)
        for i in MOTOR_PIN:
            pi.set_mode(i, pigpio.OUTPUT)

        # initialize ramps
        # 90 degrees
        ramp_90 = init_ramp(90)

        # 180 degrees
        ramp_180 = init_ramp(180)

        is_init = True


def generate_ramp(pin, ramp):
    """Generate ramp wave forms.
    ramp:  List of [Frequency, Steps]
    """
    pi.wave_clear()     # clear existing waves
    length = len(ramp)  # number of ramp levels
    wid = [-1] * length

    # Generate a wave per ramp level
    for i in range(length):
        frequency = ramp[i][0]
        micros = int(500000 / frequency)
        wf = []
        wf.append(pigpio.pulse(1 << pin, 0, micros))  # pulse on
        wf.append(pigpio.pulse(0, 1 << pin, micros))  # pulse off
        pi.wave_add_generic(wf)
        wid[i] = pi.wave_create()

    # Generate a chain of waves
    chain = []
    for i in range(length):
        steps = ramp[i][1]
        x = steps & 255
        y = steps >> 8
        chain += [255, 0, wid[i], 255, 1, x, y]

    pi.wave_chain(chain)  # Transmit chain.


# rotate 90 degrees in the specified direction (CW or CCW)
# param:motor_pin - One of UP, RIGHT, FRONT, DOWN, LEFT, or BACK, as defined above.
# param:direction - One of CW or CCW, as defined above.
def rot_90(motor_pin, direction=CW):
    if not is_init:
        init()
    pi.write(DIR, direction)
    generate_ramp(motor_pin, ramp_90)


# rotate 180 degrees in the specified direction (CW or CCW)
# param:motor_pin - One of UP, RIGHT, FRONT, DOWN, LEFT, or BACK, as defined above.
# param:direction - One of CW or CCW, as defined above. Default is CW
def rot_180(motor_pin, direction=CW):
    if not is_init:
        init()
    pi.write(DIR, direction)
    generate_ramp(motor_pin, ramp_180)


# take a recipe, of the form (e.g.) "R L2 F B U' F' D F' U B2 L' U2 B2 U D' B2 U2 L2 D' R2 D2"
# and execute it using the attached stepper motors.
def execute(recipe_str):
    recipe = recipe_str.split()
    for step_str in recipe:
        base = step_str[0]
        mot = STEP_MAP[base]
        if (len(step_str) >= 2):
            xtra = step_str[-1:]
            if (xtra == "'"):
                rot_90(mot, CCW)
            elif (xtra == "2"):
                rot_180(mot)
        else:
            rot_90(mot)


if __name__ == "__main__":
    init()
    print("Stepper test.")
    delay = 0.25

    # rotate each side 90 degrees, four times, with a pause between each rotation.
    for s, mot in zip(STEP_NAME, MOTOR_PIN):
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
