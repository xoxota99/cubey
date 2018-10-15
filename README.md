# cubey
A Raspberry pi-based Rubik's Cube solving robot.

## Thanks
All credit goes to Jay Flatland, and his [HighFrequencyTwister](https://github.com/jayflatland/HighFrequencyTwister) as the inspiration for this project. This build is just a ghetto version of Jay's project, with a bit of cleaned up documentation, EAGLE files for the relevant PCB, a BOM, and extraneous (to me) stuff removed.

## Hardware
I'm using all the same hardware and 3D-printed parts as [HighFrequencyTwister](https://github.com/jayflatland/HighFrequencyTwister) , but replaced the PC / Arduino combination with a single Raspberry pi. 

I've also created a custom PCB to tidy up the wiring of the DRV8825 carrier boards. It sits where a Raspberry pi hat would sit, but definitely does NOT conform to the RPI Hat specification (no cutouts for relevant connectors, no EEPROM for board identification, PCB is too big for a hat, etc.)

## Software
I use the same offline C implementation of the kociemba solver as [HighFrequencyTwister](https://github.com/jayflatland/HighFrequencyTwister), and all other code is written in Python, with GPIO control for stepper motor control via [piGPIO](https://github.com/joan2937/pigpio)
