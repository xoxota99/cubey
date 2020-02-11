[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=xoxota99_cubey&metric=bugs)](https://sonarcloud.io/dashboard?id=xoxota99_cubey)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=xoxota99_cubey&metric=code_smells)](https://sonarcloud.io/dashboard?id=xoxota99_cubey)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=xoxota99_cubey&metric=coverage)](https://sonarcloud.io/dashboard?id=xoxota99_cubey)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=xoxota99_cubey&metric=duplicated_lines_density)](https://sonarcloud.io/dashboard?id=xoxota99_cubey)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=xoxota99_cubey&metric=ncloc)](https://sonarcloud.io/dashboard?id=xoxota99_cubey)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=xoxota99_cubey&metric=alert_status)](https://sonarcloud.io/dashboard?id=xoxota99_cubey)

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=xoxota99_cubey&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=xoxota99_cubey)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=xoxota99_cubey&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=xoxota99_cubey)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=xoxota99_cubey&metric=security_rating)](https://sonarcloud.io/dashboard?id=xoxota99_cubey)

[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=xoxota99_cubey&metric=sqale_index)](https://sonarcloud.io/dashboard?id=xoxota99_cubey)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=xoxota99_cubey&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=xoxota99_cubey)


# cubey
A Raspberry pi-based Rubik's Cube solving robot.

## Thanks
All credit goes to Jay Flatland, and his [HighFrequencyTwister](https://github.com/jayflatland/HighFrequencyTwister) as the inspiration for this project. This build is just a ghetto version of Jay's project, with a bit of cleaned up documentation, EAGLE files for the relevant PCB, a BOM, and extraneous (to me) stuff removed.

## Hardware
I'm using all the same hardware and 3D-printed parts as [HighFrequencyTwister](https://github.com/jayflatland/HighFrequencyTwister) , but replaced the PC / Arduino combination with a single Raspberry pi. 

I've also created a [custom PCB](https://oshpark.com/shared_projects/SddnpiI5) to tidy up the wiring of the DRV8825 carrier boards. It sits where a Raspberry pi hat would sit, but definitely does NOT conform to the RPI Hat specification (no cutouts for relevant connectors, no EEPROM for board identification, PCB is too big for a hat, etc.)

## Software
I use the same offline C implementation of the kociemba solver as [HighFrequencyTwister](https://github.com/jayflatland/HighFrequencyTwister), and all other code is written in Python, with GPIO control for stepper motor control via [piGPIO](https://github.com/joan2937/pigpio). Cubey uses a single camera for Cube State estimation, which simplifies calibration, but impacts speed. Cubey definitely *won't* set any world speed records.
