from cubey.config import cfg
from cubey import stepper
import pigpio
import time
import sys
import os
import logging


logging.basicConfig(
    level=logging.getLevelName(cfg['app']['logLevel']), format=cfg['app']['logFormat'])


"""
Utility for interactively commanding the Stepper motors of the robot, using typical Rubik's Cube commands:
R - Turn RIGHT face clockwise 90 degrees
R2 - Turn RIGHT face 180 degrees (in an undefined direction)
R' - Turn RIGHT face counter-clockwise 90 degrees.

For "R" above, you can substitute any of:
F - FRONT face
U - UP face
L - LEFT face
B - BACK face
D - DOWN face

You can chain together commands in a single line, such as: D2 R2 U L' B' D R L' B U2 F L2 U2 L2 U' F2 D' B2 U' B2 U2 

"""

if __name__ == "__main__":

    from cmd import Cmd

    class MyPrompt(Cmd):

        def default(self, inp):
            if inp == "Q" or inp == "EOF":
                return self.do_q(inp)

            recipe = inp.upper().split()
            for step_str in recipe:
                base = step_str[0]
                if stepper.FACE_NAME[base]:
                    if (len(step_str) >= 2):
                        xtra = step_str[-1:]
                        print(base+xtra)
                        if (xtra == "'"):
                            stepper.rot_90(
                                stepper.FACE_MOTOR_MAP[base], stepper.CCW)
                        elif (xtra == "2"):
                            stepper.rot_180(stepper.FACE_MOTOR_MAP[base])
                    else:
                        stepper.rot_90(stepper.FACE_MOTOR_MAP[base])
                        print(base)
                else:
                    print("*** Unknown cube face '" + base +
                          "' in move '" + step_str + "'")

        def do_q(self, inp):
            print("Bye")
            return True

    p = MyPrompt()
    p.prompt = "Cubey > "
    p.cmdloop()

    pi.stop()
