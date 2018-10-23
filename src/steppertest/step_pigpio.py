#!/usr/bin/env python

import time
import pigpio

UP = 14
RIGHT = 18
FRONT = 21
DOWN = 16
LEFT = 20
BACK = 23

STEP_MAP = {
    "U": UP,
    "R": RIGHT,
    "F": FRONT,
    "D": DOWN,
    "L": LEFT,
    "B": BACK
}

# STEP = RIGHT
DIR = 15
CW = 0
CCW = 1

SPR = 200  # steps per revolution
STEP_FACTOR = 8  # micro-stepping at 1/8

faces = [UP, RIGHT, FRONT, DOWN, LEFT, BACK]
dirnames = ["CW", "CCW"]


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


if __name__ == "__main__":
    speed = 4000
    pi = pigpio.pi()
    if not pi.connected:
        print("NOT CONNECTED.")
        exit()

    pi.set_mode(DIR, pigpio.OUTPUT)
    for mot in faces:
        pi.set_mode(mot, pigpio.OUTPUT)

    from cmd import Cmd

    class MyPrompt(Cmd):

        def default(self, inp):
            if inp == "Q" or inp == "EOF":
                return self.do_q(inp)

            recipe = inp.upper().split()
            for step_str in recipe:
                base = step_str[0]
                if base in STEP_MAP:
                    pin = STEP_MAP[base]
                    if (len(step_str) >= 2):
                        xtra = step_str[-1:]
                        print(base+xtra)
                        if (xtra == "'"):
                            pi.write(DIR, CCW)
                            tx_pulses(pi, pin, speed, SPR * STEP_FACTOR // 4)
                        elif (xtra == "2"):
                            pi.write(DIR, CW)
                            tx_pulses(pi, pin, speed, SPR * STEP_FACTOR // 2)
                    else:
                        pi.write(DIR, CW)
                        print(base)
                        tx_pulses(pi, pin, speed, SPR * STEP_FACTOR // 4)
                else:
                    print("*** Unknown cube face '" + base +
                          "' in move '" + step_str + "'")
                    # return True

        def do_q(self, inp):
            print("Bye")
            return True

    p = MyPrompt()
    p.prompt = "Cubey > "
    p.cmdloop()

    pi.stop()
