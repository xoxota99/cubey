from time import sleep
import RPi.GPIO as GPIO


UP = 14
RIGHT = 18
FRONT = 21
DOWN = 16
LEFT = 20
BACK = 23

STEP = UP           # STEP GPIO pin
DIR = 15                # Direction GPIO Pin

CW = 1     # Clockwise Rotation
CCW = 0    # Counterclockwise Rotation
SPR = 200   # Steps per Revolution (360 / 7.5)

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.output(DIR, CW)

# MODE = (14, 15, 18)   # Microstep Resolution GPIO Pins
# GPIO.setup(MODE, GPIO.OUT)
# RESOLUTION = {'Full': (0, 0, 0),
#               'Half': (1, 0, 0),
#               '1/4': (0, 1, 0),
#               '1/8': (1, 1, 0),
#               '1/16': (0, 0, 1),
#               '1/32': (1, 0, 1)}

# GPIO.output(MODE, RESOLUTION['1/32'])

STEP_FACTOR = 8

step_count = int(SPR * STEP_FACTOR)
delay = .00002  # sleep time between pulses.

print("delay is {:.10f} uS".format(delay * 1000000))
for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    sleep(delay)

sleep(1)
GPIO.output(DIR, CCW)
for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    sleep(delay)

GPIO.cleanup()
