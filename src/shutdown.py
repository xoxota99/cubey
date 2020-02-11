#!/usr/bin/python3

# Used to safely shutdown the pi by pushing a momentary switch. Also indicates "power" with an LED

from RPi import GPIO
import time
from subprocess import call

"""
Shutdown script, to enable a pushbutton and an LED, via GPIO. Behavior is:
- LED lights up when the RPI powers up, turns off when the RPI turns off.
- Button can be pressed (once the LED is ON) to shutdown the RPI.

After shutting down, the LED will turn off, but disk activity may continue 
for up to ten seconds. Don't actually remove power from the RPI until disk activity stops.

"""

# The GPIO pin that the button is connected to. (The other end of the button is connected to ground.)
butPin = 4
# The GPIO pin connected to the GROUND leg of the LED. The other end is connected to 5V.
ledPin = 14     # You may have to disable UART to use this pin.


def shut_down(channel):
    print("Shutting Down")
    call("sudo shutdown -P now", shell=True)


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(butPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ledPin, GPIO.OUT, initial=GPIO.LOW)  # turn on the LED.

    # Add our function to execute when the button pressed event happens
    GPIO.add_event_detect(butPin, GPIO.FALLING,
                          callback=shut_down, bouncetime=2000)
    # Now wait!
    while 1:
        time.sleep(1)


if __name__ == "__main__":
    main()
