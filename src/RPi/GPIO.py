# Mock RPi.GPIO module, so pyLint stops complaining when developing on PC / Mac.
BOARD = 1
OUT = 1
IN = 1
BCM = 1
PUD_UP = 1
HI = 1
LOW = 0
FALLING = 1


def setmode(a):
    print(a)


def setup(a, b, pull_up_down=None, initial=None):
    print(a)


def output(a, b):
    print(a)


def cleanup():
    print('cleanup')


def getmode(a):
    print(a)


def setwarnings(flag):
    print('False')


def add_event_detect(a, b, callback=None, bouncetime=0):
    print(a)
