#!/usr/bin/env python

import time
import pigpio


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
            time.sleep(0.01)
        pi.wave_delete(wid)


pi = pigpio.pi()
if not pi.connected:
    print("NOT CONNECTED.")
    exit()

STEP = 18
DIR = 17
CW = 1
CCW = 0

SPR = 200  # steps per revolution
STEP_FACTOR = 8  # micro-stepping at 1/8
step_count = SPR * STEP_FACTOR

pi.set_mode(STEP, pigpio.OUTPUT)
pi.set_mode(DIR, pigpio.OUTPUT)
pi.write(DIR, CW)

tx_pulses(pi, STEP, 1000, step_count)  # 250 pulses @ 1000 Hz
time.sleep(1)

tx_pulses(pi, STEP, 4000, step_count)  # 2391 pulses @ 5000 Hz
time.sleep(1)

tx_pulses(pi, STEP, 5000, step_count)  # 2391 pulses @ 5000 Hz
time.sleep(1)

tx_pulses(pi, STEP, 8000, step_count)  # 2391 pulses @ 5000 Hz
time.sleep(1)

pi.stop()
