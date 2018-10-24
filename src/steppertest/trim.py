#!/usr/bin/env python

# utility for "trimming" individual motors by a specific number of steps.
import time
import pigpio
import sys


def tx_pulses(pi, GPIO, hertz, num, pulse_len=1):
    assert hertz < 500000
    length_us = int(1000000/hertz)
    assert int(pulse_len) < length_us
    assert num < 65536

    num_low = num % 256
    num_high = num // 256

    wf = []

    wf.append(pigpio.pulse(1 << GPIO, 0, pulse_len))
    wf.append(pigpio.pulse(0, 1 << GPIO, length_us - pulse_len))

    pi.wave_add_generic(wf)

    wid = pi.wave_create()

    if wid >= 0:
        pi.wave_chain([255, 0, wid, 255, 1, num_low, num_high])
        while pi.wave_tx_busy():
            pass
        pi.wave_delete(wid)


pi = pigpio.pi()
if not pi.connected:
    print("NOT CONNECTED.")
    exit()

UP = 18
RIGHT = 3
FRONT = 14
DOWN = 5
LEFT = 4
BACK = 2
STEP_MAP = {
    "U": UP,
    "D": DOWN,
    "F": FRONT,
    "B": BACK,
    "L": LEFT,
    "R": RIGHT
}
# STEP = RIGHT
DIR = 15
CW = 1
CCW = 0

SPR = 200  # steps per revolution
STEP_FACTOR = 1  # micro-stepping at 1/8

pi.set_mode(DIR, pigpio.OUTPUT)
face = FRONT
DIR_MAP = {
    "CW": CW,
    "CCW": CCW
}

if (len(sys.argv)) < 4:
    print("Usage: python trim.py [U|D|F|B|L|R] [CW|CCW] <stepcount>")
    sys.exit(0)

mot = STEP_MAP[sys.argv[1]]
d = DIR_MAP[sys.argv[2]]
step_count = int(sys.argv[3])

speed = 200


pi.write(DIR, d)
pi.set_mode(mot, pigpio.OUTPUT)
tx_pulses(pi, mot, speed, step_count)

pi.stop()
