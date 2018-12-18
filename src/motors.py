import logging
from cubey import stepper
from cmd import Cmd
import yaml

"""
Utility for interactively commanding the Stepper motors of the robot, using typical Rubik's Cube notation:
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

config = {}
motors = None


class MyPrompt(Cmd):

    def default(self, inp):

        if inp == "Q" or inp == "EOF":
            return self.do_q(inp)

        recipe = inp.upper().split()
        for step_str in recipe:
            base = step_str[0]
            if base in stepper.FACE_NAME:
                motor_pin = stepper.FACE_MOTOR_MAP.get(base)
                if (len(step_str) >= 2):
                    xtra = step_str[-1:]
                    print(base+xtra)
                    if (xtra == "'"):
                        motors.rot_90(motor_pin, stepper.CCW)
                    elif (xtra == "2"):
                        motors.rot_180(motor_pin)
                else:
                    motors.rot_90(motor_pin)
                    print(base)
            else:
                print("*** Unknown cube face '" + base +
                      "' in move '" + step_str + "'")

    def do_q(self, inp):
        print("Bye")
        return True


if __name__ == "__main__":
    config_file = "config.yaml"
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    motors = stepper.MotorController(config)

    p = MyPrompt()

    p.prompt = "Cubey > "
    p.cmdloop()

    # pi.stop()   #it may be that horrible things will happen if we don't call stop.
