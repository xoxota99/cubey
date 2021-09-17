#!/usr/bin/env python3
import pigpio
import time
from subprocess import call

"""
Shutdown script, to enable a pushbutton and an LED, via GPIO. Behavior is:
- LED lights up when the RPI powers up, turns off when the RPI turns off.
- Button can be pressed (once the LED is ON) to shutdown the RPI.

After shutting down, the LED will turn off, but disk activity may continue 
for up to ten seconds. Don't actually remove power from the RPI until disk activity stops.

"""

# The GPIO pin that the button is connected to. (Active LOW)
butPin = 4

# The GPIO pin connected to the GROUND leg of the LED. The other end is connected to 5V.
ledPin = 14     # You may have to disable UART to use pin 14.


def shut_down(gpio, level, tick):
    print("Shutting Down")
    call("sudo shutdown -P now", shell=True)


def main():
    pi = pigpio.pi()
    pi.set_mode(butPin, pigpio.INPUT)   # set as input
    pi.set_pull_up_down(butPin, pigpio.PUD_UP)  # set internal pullup
    pi.set_glitch_filter(butPin, 300000)    # debounce 0.3 seconds

    # Add our function to execute when the button pressed event happens
    pi.callback(butPin, pigpio.FALLING_EDGE, shut_down)

    pi.set_mode(ledPin, pigpio.OUTPUT)
    pi.write(ledPin, 0)  # inverted signal. zero is lit, 1 is unlit.

    # Now wait!
    while 1:
        time.sleep(1)


if __name__ == "__main__":
    main()
