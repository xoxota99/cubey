# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Cubey robot.

## Diagnostic Tools

Cubey includes several diagnostic commands to help identify issues:

```bash
# Check system status
cubey status

# Test camera functionality
cubey test camera

# Test motor functionality
cubey test motors

# Validate configuration
cubey validate-config
```

## Common Issues

### Hardware Issues

#### Camera Problems

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Camera not detected | • Camera not connected<br>• Camera disabled in Raspberry Pi config<br>• Wrong device ID | • Check physical connection<br>• Run `sudo raspi-config` and enable camera<br>• Try different device IDs in config |
| Blurry images | • Dirty lens<br>• Camera out of focus<br>• Poor lighting | • Clean the lens<br>• Adjust focus ring if available<br>• Improve lighting conditions |
| Color detection issues | • Inconsistent lighting<br>• Reflections<br>• Worn cube stickers | • Use diffused lighting<br>• Adjust camera position<br>• Replace cube or stickers |

#### Motor Problems

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Motors not moving | • Power issues<br>• Incorrect wiring<br>• Wrong GPIO pins | • Check power supply<br>• Verify connections<br>• Update pin configuration |
| Motors moving in wrong direction | • Incorrect direction pin setting<br>• Reversed wiring | • Toggle direction in config<br>• Check motor wiring |
| Inconsistent movement | • Insufficient power<br>• Mechanical binding<br>• Loose connections | • Use adequate power supply<br>• Check for mechanical issues<br>• Secure all connections |
| Loud noise from motors | • Excessive speed<br>• Mechanical issues<br>• Resonance | • Reduce speed in config<br>• Check for binding<br>• Add damping material |

#### Mechanical Problems

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Cube slipping | • Loose grippers<br>• Worn cube | • Adjust gripper tension<br>• Replace cube |
| Frame instability | • Loose screws<br>• Warped components | • Tighten all fasteners<br>• Reinforce or replace parts |
| Misaligned faces | • Motor mount issues<br>• Frame distortion | • Realign motor mounts<br>• Check frame for squareness |

### Software Issues

#### Configuration Problems

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Configuration errors | • Syntax errors in YAML<br>• Missing required fields<br>• Invalid values | • Validate YAML syntax<br>• Check against example config<br>• Run `cubey validate-config` |
| Camera calibration issues | • Incorrect calibration file<br>• Changed lighting conditions | • Recalibrate with `cubey calibrate`<br>• Ensure consistent lighting |
| Motor configuration issues | • Wrong pin assignments<br>• Incorrect motor parameters | • Verify GPIO pin numbers<br>• Adjust motor speed and timing |

#### Solver Problems

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Invalid cube state | • Scanning errors<br>• Incorrect color detection | • Improve lighting<br>• Recalibrate camera<br>• Check cube positioning |
| Solver fails to find solution | • Impossible cube state<br>• Timeout too short | • Verify cube is valid<br>• Increase solver timeout in config |
| Solution not executed correctly | • Motor timing issues<br>• Cube slipping | • Adjust motor speed<br>• Check cube grippers |

#### Web Interface Problems

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Web server won't start | • Port already in use<br>• Missing dependencies | • Change port in config<br>• Install required packages |
| Cannot access web interface | • Firewall blocking access<br>• Wrong IP address | • Check firewall settings<br>• Verify IP address |
| Video stream not working | • Camera issues<br>• Network bandwidth | • Check camera functionality<br>• Reduce resolution |

## Advanced Troubleshooting

### Logging

Cubey creates detailed logs that can help diagnose issues:

```bash
# View the log file
cat cubey.log

# Increase log verbosity
cubey --log-level DEBUG solve
```

### GPIO Debugging

To test GPIO pins directly:

```bash
# Install GPIO utilities
sudo apt install python3-gpiozero

# Test a specific pin (replace 19 with your pin number)
python3 -c "from gpiozero import LED; led = LED(19); led.on(); input('Press Enter to continue...'); led.off()"
```

### Camera Debugging

To test the camera directly:

```bash
# Capture a still image
raspistill -o test.jpg

# Display a live preview
raspivid -t 0
```

### System Resources

Check if resource constraints are causing issues:

```bash
# Check CPU usage
top

# Check memory usage
free -h

# Check disk space
df -h

# Check temperature
vcgencmd measure_temp
```

## Getting Help

If you're still experiencing issues:

1. Check the [GitHub Issues](https://github.com/cubey/cubey/issues) for similar problems
2. Join the [Cubey Discord server](https://discord.gg/cubey) for community support
3. Create a new issue with:
   - Detailed description of the problem
   - Steps to reproduce
   - Log files
   - Configuration files (with sensitive information removed)
   - Photos or videos of the issue (for hardware problems)
