from lib.motorcontroller import MotorController
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


class MyPrompt(Cmd):

    def __init__(self, motors):
        self.motors = motors
        super(MyPrompt, self).__init__()

    def default(self, inp):
        if inp == "Q" or inp == "EOF":
            return self.do_q(inp)

        self.motors.execute(inp.upper())

    def emptyline(self):
        # do nothing.
        pass

    def do_q(self, inp):
        print("Bye")
        return True


if __name__ == "__main__":
    config_file = "config.yaml"
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    motors = MotorController(config)

    print("""
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
    
    """)

    p = MyPrompt(motors)

    p.prompt = "Cubey > "
    p.cmdloop()

    # it may be that horrible things will happen if we don't call stop.
    motors._stop()
