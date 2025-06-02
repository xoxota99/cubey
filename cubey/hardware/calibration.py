"""
Calibration module for the Cubey robot
"""

import logging
import os
import yaml
from typing import Dict, Any, Optional

import numpy as np

from cubey.exceptions import CalibrationError
from cubey.hardware.camera import Camera
from cubey.hardware.motorcontroller import MotorController

def collision_detect(colors: Dict[str, Dict[str, np.ndarray]]) -> list:
    """
    Detect collisions in HSV color ranges
    
    Args:
        colors: Dictionary of color ranges
        
    Returns:
        List of collisions
    """
    logger = logging.getLogger(__name__)
    collisions = []
    keys = ["U", "R", "F", "D", "L", "B"]

    for i in range(0, 6):
        bracket1 = colors[keys[i]]
        for j in range(i + 1, 6):
            bracket2 = colors[keys[j]]
            collide = False

            # Check for hue overlap, handling the special case of red
            if bracket1["max"][0] < bracket1["min"][0]:  # Red wraps around
                collide = (bracket1["max"][0] > bracket2["min"][0]) or (
                    bracket1["min"][0] < bracket2["max"][0])
            elif bracket2["max"][0] < bracket2["min"][0]:  # Red wraps around
                collide = (bracket2["max"][0] > bracket1["min"][0]) or (
                    bracket2["min"][0] < bracket1["max"][0])
            else:
                # Non-red. Do these hues overlap?
                collide = (bracket1["max"][0] > bracket2["min"][0]) and (
                    bracket1["min"][0] < bracket2["max"][0])

            # Check for saturation and value overlap
            collide = collide and (
                bracket1["max"][1] > bracket2["min"][1]) and (
                bracket1["min"][1] < bracket2["max"][1]) and (
                bracket1["max"][2] > bracket2["min"][2]) and (
                bracket1["min"][2] < bracket2["max"][2])

            if collide:
                collisions.append(
                    {
                        keys[i]: [bracket1["min"].tolist(), bracket1["max"].tolist()],
                        keys[j]: [bracket2["min"].tolist(), bracket2["max"].tolist()],
                    }
                )

    if collisions:
        logger.warning("-----------------------------------------------")
        logger.warning("There were collisions in the HSV calibration:")
        for c in collisions:
            logger.warning(f"\t{c}")
        logger.warning("-----------------------------------------------")
        
    return collisions

def calibrate(config: Dict[str, Any], output_file: Optional[str] = None) -> int:
    """
    Calibrate the scanner
    
    Args:
        config: Configuration dictionary
        output_file: Optional output file for calibration data
        
    Returns:
        Exit code
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting calibration...")
    
    try:
        # Load existing calibration data
        calib_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                 "config", config["cam"]["calibration"])
        
        with open(calib_file, "r") as f:
            calib_data = yaml.safe_load(f)
            
        # Initialize hardware
        camera = Camera(config, calib_data)
        motors = MotorController(config)
        
        # Dictionary to store HSV values for each face
        facelet_hsv = {
            "U": np.zeros((9, 3)).tolist(),
            "R": np.zeros((9, 3)).tolist(),
            "F": np.zeros((9, 3)).tolist(),
            "D": np.zeros((9, 3)).tolist(),
            "L": np.zeros((9, 3)).tolist(),
            "B": np.zeros((9, 3)).tolist()
        }
        
        # Scan front and right faces
        logger.info("Scanning front and right faces...")
        hsv_values = camera.get_raw_hsv("calib_FR.jpg")
        facelet_hsv["F"][0], facelet_hsv["R"][1], facelet_hsv["F"][2] = hsv_values[:3]
        facelet_hsv["F"][3], facelet_hsv["R"][4], facelet_hsv["F"][5] = hsv_values[3:]
        
        # Rotate to scan front and left faces
        logger.info("Rotating to scan front and left faces...")
        motors.execute("F2")
        hsv_values = camera.get_raw_hsv("calib_FL.jpg")
        _, facelet_hsv["L"][1], _ = hsv_values[:3]
        _, facelet_hsv["L"][4], _ = hsv_values[3:]
        
        # Rotate to scan front and down faces
        logger.info("Rotating to scan front and down faces...")
        motors.execute("F")
        hsv_values = camera.get_raw_hsv("calib_FD.jpg")
        _, facelet_hsv["D"][1], _ = hsv_values[:3]
        _, facelet_hsv["D"][4], _ = hsv_values[3:]
        
        # Rotate to scan down face
        logger.info("Rotating to scan down face...")
        motors.execute("F R")
        hsv_values = camera.get_raw_hsv("calib_D.jpg")
        facelet_hsv["D"][0], _, facelet_hsv["D"][2] = hsv_values[:3]
        facelet_hsv["D"][3], _, facelet_hsv["D"][5] = hsv_values[3:]
        
        # Rotate to scan up and back faces
        logger.info("Rotating to scan up and back faces...")
        motors.execute("R' U R'")
        hsv_values = camera.get_raw_hsv("calib_UB.jpg")
        facelet_hsv["U"][0], facelet_hsv["B"][1], facelet_hsv["U"][2] = hsv_values[:3]
        facelet_hsv["U"][3], facelet_hsv["B"][4], facelet_hsv["U"][5] = hsv_values[3:]
        
        # Rotate to scan right and front faces again
        logger.info("Rotating to scan right and front faces again...")
        motors.execute("R U' R U F")
        hsv_values = camera.get_raw_hsv("calib_RF.jpg")
        facelet_hsv["R"][0], facelet_hsv["F"][1], facelet_hsv["R"][2] = hsv_values[:3]
        facelet_hsv["R"][3], facelet_hsv["F"][4], facelet_hsv["R"][5] = hsv_values[3:]
        
        # Rotate to scan left face
        logger.info("Rotating to scan left face...")
        motors.execute("F' U' R' U' F")
        hsv_values = camera.get_raw_hsv("calib_L.jpg")
        facelet_hsv["L"][0], _, facelet_hsv["L"][2] = hsv_values[:3]
        facelet_hsv["L"][3], _, facelet_hsv["L"][5] = hsv_values[3:]
        
        # Rotate to scan back and up faces
        logger.info("Rotating to scan back and up faces...")
        motors.execute("F' U' F")
        hsv_values = camera.get_raw_hsv("calib_BU.jpg")
        facelet_hsv["B"][0], facelet_hsv["U"][1], facelet_hsv["B"][2] = hsv_values[:3]
        facelet_hsv["B"][3], facelet_hsv["U"][4], facelet_hsv["B"][5] = hsv_values[3:]
        
        # Return to the original position
        logger.info("Returning to original position...")
        motors.execute("F' U2")
        
        # Build calibration data
        logger.info("Building calibration data...")
        colors = {}
        for key in facelet_hsv:
            # Convert lists to numpy arrays for easier min/max calculation
            hsv_arrays = [np.array(hsv) for hsv in facelet_hsv[key] if sum(hsv) > 0]
            
            if not hsv_arrays:
                logger.warning(f"No HSV values for face {key}")
                continue
                
            # Calculate min and max HSV values
            min_hsv = np.min(hsv_arrays, axis=0)
            max_hsv = np.max(hsv_arrays, axis=0)
            
            # Add some margin
            min_hsv = np.maximum(min_hsv - np.array([5, 20, 20]), np.array([0, 0, 0]))
            max_hsv = np.minimum(max_hsv + np.array([5, 20, 20]), np.array([180, 255, 255]))
            
            colors[key] = {
                "min": min_hsv,
                "max": max_hsv
            }
            
        # Check for collisions
        collisions = collision_detect(colors)
        if collisions:
            logger.warning(f"Found {len(collisions)} color collisions")
            
        # Get camera settings
        camera_settings = Camera.get_settings()
        
        # Create calibration object
        calibration = {
            "camera": camera_settings,
            "colors": {k: {"min": v["min"].tolist(), "max": v["max"].tolist()} for k, v in colors.items()},
            "sample_aperture": config["cam"]["sample_aperture"]
        }
        
        # Save calibration data
        if output_file:
            with open(output_file, "w") as f:
                yaml.dump(calibration, f)
            logger.info(f"Calibration data saved to {output_file}")
        else:
            logger.info("Calibration data:")
            logger.info(yaml.dump(calibration))
            
        # Clean up
        camera.close()
        
        return 0
    except Exception as e:
        logger.error(f"Calibration failed: {e}")
        return 1
