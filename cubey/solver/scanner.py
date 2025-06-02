"""
Scanner for the Cubey robot
"""

import logging
from typing import Dict, Any, List, Optional

from cubey.exceptions import ScannerError
from cubey.hardware.camera import Camera
from cubey.hardware.motorcontroller import MotorController

class Scanner:
    """
    Scanner for detecting the state of the cube
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the scanner
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Load calibration data
        import os
        import yaml
        
        calib_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                 "config", config["cam"]["calibration"])
        
        try:
            with open(calib_file, "r") as f:
                self.calib_data = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading calibration data: {e}")
            raise ScannerError(f"Failed to load calibration data: {e}")
            
        self.camera = None
        
    def _init_camera(self) -> None:
        """
        Initialize the camera if not already initialized
        
        Raises:
            ScannerError: If the camera cannot be initialized
        """
        if self.camera is None:
            try:
                self.camera = Camera(self.config, self.calib_data)
            except Exception as e:
                self.logger.error(f"Error initializing camera: {e}")
                raise ScannerError(f"Failed to initialize camera: {e}")
                
    def _release_camera(self) -> None:
        """
        Release camera resources
        """
        if self.camera is not None:
            self.camera.close()
            self.camera = None
            
    def scan_state(self, motors: MotorController) -> Dict[str, List[str]]:
        """
        Scan the current state of the cube
        
        Args:
            motors: Motor controller for manipulating the cube
            
        Returns:
            Dictionary mapping face names to lists of colors
            
        Raises:
            ScannerError: If the scan fails
        """
        self.logger.info("Scanning cube state")
        
        try:
            self._init_camera()
            
            # Dictionary to store the colors of each face
            faces = {
                "U": ["X"] * 9,
                "R": ["X"] * 9,
                "F": ["X"] * 9,
                "D": ["X"] * 9,
                "L": ["X"] * 9,
                "B": ["X"] * 9
            }
            
            # Scan front and right faces
            row1, row2 = self.camera.get_faces("scan_FR.jpg")
            faces["F"][0], faces["R"][1], faces["F"][2] = row1
            faces["F"][3], faces["R"][4], faces["F"][5] = row2
            self.logger.debug(f"Scanned F/R: {row1}, {row2}")
            
            # Rotate to scan front and left faces
            motors.execute("F2")
            row1, row2 = self.camera.get_faces("scan_FL.jpg")
            _, faces["L"][1], _ = row1
            _, faces["L"][4], _ = row2
            self.logger.debug(f"Scanned F/L: {row1}, {row2}")
            
            # Rotate to scan front and down faces
            motors.execute("F")
            row1, row2 = self.camera.get_faces("scan_FD.jpg")
            _, faces["D"][1], _ = row1
            _, faces["D"][4], _ = row2
            self.logger.debug(f"Scanned F/D: {row1}, {row2}")
            
            # Rotate to scan down face
            motors.execute("F R")
            row1, row2 = self.camera.get_faces("scan_D.jpg")
            faces["D"][0], _, faces["D"][2] = row1
            faces["D"][3], _, faces["D"][5] = row2
            self.logger.debug(f"Scanned D: {row1}, {row2}")
            
            # Rotate to scan up and back faces
            motors.execute("R' U R'")
            row1, row2 = self.camera.get_faces("scan_UB.jpg")
            faces["U"][0], faces["B"][1], faces["U"][2] = row1
            faces["U"][3], faces["B"][4], faces["U"][5] = row2
            self.logger.debug(f"Scanned U/B: {row1}, {row2}")
            
            # Rotate to scan right and front faces again
            motors.execute("R U' R U F")
            row1, row2 = self.camera.get_faces("scan_RF.jpg")
            faces["R"][0], faces["F"][1], faces["R"][2] = row1
            faces["R"][3], faces["F"][4], faces["R"][5] = row2
            self.logger.debug(f"Scanned R/F: {row1}, {row2}")
            
            # Rotate to scan left face
            motors.execute("F' U' R' U' F")
            row1, row2 = self.camera.get_faces("scan_L.jpg")
            faces["L"][0], _, faces["L"][2] = row1
            faces["L"][3], _, faces["L"][5] = row2
            self.logger.debug(f"Scanned L: {row1}, {row2}")
            
            # Rotate to scan back and up faces
            motors.execute("F' U' F")
            row1, row2 = self.camera.get_faces("scan_BU.jpg")
            faces["B"][0], faces["U"][1], faces["B"][2] = row1
            faces["B"][3], faces["U"][4], faces["B"][5] = row2
            self.logger.debug(f"Scanned B/U: {row1}, {row2}")
            
            # Return to the original position
            motors.execute("F' U2")
            
            # Fill in the center pieces (these are fixed)
            faces["U"][4] = "U"
            faces["R"][4] = "R"
            faces["F"][4] = "F"
            faces["D"][4] = "D"
            faces["L"][4] = "L"
            faces["B"][4] = "B"
            
            return faces
        except Exception as e:
            self.logger.error(f"Error scanning cube: {e}")
            raise ScannerError(f"Failed to scan cube: {e}")
        finally:
            self._release_camera()
            
    def get_state_string(self, motors: MotorController) -> Optional[str]:
        """
        Get a string representation of the cube state
        
        Args:
            motors: Motor controller for manipulating the cube
            
        Returns:
            String representation of the cube state, or None if invalid
        """
        try:
            faces = self.scan_state(motors)
            
            # Convert the faces dictionary to a string in the format expected by the solver
            # The order is: U, R, F, D, L, B
            state = ""
            for face in ["U", "R", "F", "D", "L", "B"]:
                state += "".join(faces[face])
                
            # Validate the state
            if self._validate_state(state):
                return state
            else:
                self.logger.error("Invalid cube state detected")
                return None
        except Exception as e:
            self.logger.error(f"Error getting state string: {e}")
            return None
            
    def _validate_state(self, state: str) -> bool:
        """
        Validate a cube state
        
        Args:
            state: String representation of the cube state
            
        Returns:
            True if the state is valid, False otherwise
        """
        if not state or len(state) != 54:
            self.logger.error(f"Invalid state length: {len(state) if state else 0}, expected 54")
            return False
            
        # Check if the state contains only valid colors
        valid_colors = set("URFDLB")
        if not all(c in valid_colors for c in state):
            self.logger.error(f"Invalid colors in state: {set(state) - valid_colors}")
            return False
            
        # Check if the state has the correct number of each color
        for color in valid_colors:
            if state.count(color) != 9:
                self.logger.error(f"Invalid color count for {color}: {state.count(color)}, expected 9")
                return False
                
        return True
