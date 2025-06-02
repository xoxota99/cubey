# Hardware Assembly Guide

This guide provides detailed instructions for assembling the Cubey hardware components.

## Components Overview

![Components Diagram](images/components_diagram.png)

*Note: The image above is a reference diagram. Your actual components may vary slightly.*

## Required Tools

- Phillips screwdriver
- Wire cutters/strippers
- Soldering iron and solder (for some connections)
- Allen wrenches (for frame assembly)
- Multimeter (for testing connections)

## Assembly Steps

### 1. Frame Assembly

The frame consists of several 3D-printed parts that hold the cube and motors in place.

![Frame Assembly](images/frame_assembly.png)

1. Print all frame components using the STL files in the `hardware/3d_models` directory
2. Assemble the base plate and vertical supports
3. Attach the motor mounts to the frame
4. Secure all connections with M3 screws

### 2. Motor Installation

Each face of the cube requires one stepper motor to rotate it.

![Motor Installation](images/motor_installation.png)

1. Insert each stepper motor into its corresponding mount
2. Secure motors with screws, ensuring they're firmly attached
3. Attach the cube grippers to each motor shaft
   - For NEMA 17 motors: Use the 3D-printed shaft connectors

### 3. Electronics Wiring

The wiring connects the motors to their drivers and the Raspberry Pi.

![Wiring Diagram](images/wiring_diagram.png)

#### Raspberry Pi GPIO Pinout

| Component | GPIO Pin | Physical Pin |
| --------- | -------- | ------------ |
| U Face    | GPIO 19  | 35           |
| R Face    | GPIO 10  | 19           |
| F Face    | GPIO 3   | 5            |
| D Face    | GPIO 13  | 33           |
| L Face    | GPIO 22  | 15           |
| B Face    | GPIO 2   | 3            |
| Disable   | GPIO 6   | 31           |
| Direction | GPIO 26  | 37           |

#### Stepper Motor Driver Connections

For NEMA 17 motors with A4988 drivers:

1. Connect the motor coils to the driver outputs (A1, A2, B1, B2)
2. Connect the driver STEP pin to the corresponding Raspberry Pi GPIO pin
3. Connect the driver DIR pin to the direction GPIO pin
4. Connect the driver ENABLE pin to the disable GPIO pin
5. Connect the driver to the 12V power supply

### 4. Camera Mounting

The camera needs to be positioned to clearly see the cube faces.

![Camera Mounting](images/camera_mounting.png)

1. Attach the camera mount to the frame
2. Connect the camera to the Raspberry Pi using the ribbon cable
3. Adjust the camera position to ensure all visible cube faces are in frame
4. Secure the camera in place

### 5. Lighting Setup (Optional)

Consistent lighting improves color detection accuracy.

![Lighting Setup](images/lighting_setup.png)

1. Attach LED strips to the frame around the cube
2. Connect the LEDs to a power source
3. Position the lights to minimize shadows and reflections

### 6. Final Assembly

1. Place the Raspberry Pi in its mount on the frame
2. Secure all wiring with cable ties or clips
3. Double-check all connections
4. Connect the power supplies

## Testing the Assembly

After completing the assembly, perform these tests:

1. **Power Test**: Connect power and ensure all components receive proper voltage
2. **Motor Test**: Run `cubey test motors` to verify each motor works correctly
3. **Camera Test**: Run `cubey test camera` to check camera positioning
4. **Full System Test**: Run `cubey solve` with a scrambled cube

## Troubleshooting

### Motors Not Moving

- Check wiring connections
- Verify power supply voltage
- Ensure GPIO pins are correctly configured in software

### Camera Issues

- Check ribbon cable connection
- Adjust camera position
- Ensure adequate lighting

### Mechanical Problems

- Check for binding or friction in moving parts
- Verify motor mounts are secure
- Ensure cube grippers hold the cube firmly but not too tightly

## Maintenance

- Periodically check and tighten screws
- Clean camera lens regularly
- Inspect wiring for wear or damage
- Lubricate moving parts if necessary

## Customization

The basic design can be customized for different cube sizes or motor types:

- For 2x2 cubes: Use the smaller frame components
- For larger cubes: Scale up the frame and use stronger motors
- For different motor types: Use the appropriate adapters and update the configuration
