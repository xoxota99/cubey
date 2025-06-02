"""
Camera module for the Cubey robot
"""

import logging
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import cv2

from cubey.exceptions import CameraError

def test_color(hsv: np.ndarray, min_hsv: np.ndarray, max_hsv: np.ndarray) -> bool:
    """
    Test if a color is within the specified HSV range
    
    Args:
        hsv: HSV color to test
        min_hsv: Minimum HSV values
        max_hsv: Maximum HSV values
        
    Returns:
        True if the color is within the range, False otherwise
    """
    h, s, v = hsv
    h_min, s_min, v_min = min_hsv
    h_max, s_max, v_max = max_hsv
    
    # Special case for red, which wraps around the hue circle
    if h_min > h_max:
        return ((h >= h_min) or (h <= h_max)) and (s >= s_min) and (s <= s_max) and (v >= v_min) and (v <= v_max)
    else:
        return (h >= h_min) and (h <= h_max) and (s >= s_min) and (s <= s_max) and (v >= v_min) and (v <= v_max)

def guess_color(hsv: np.ndarray, colors: Dict[str, Dict[str, np.ndarray]]) -> str:
    """
    Guess the color of a pixel based on HSV values
    
    Args:
        hsv: HSV color to guess
        colors: Dictionary of color ranges
        
    Returns:
        Color name or 'X' if unknown
    """
    for color_name, color_range in colors.items():
        if test_color(hsv, color_range["min"], color_range["max"]):
            return color_name
    
    return "X"  # Unknown color

class Camera:
    """
    Camera class for capturing and processing images of the cube
    """
    
    def __init__(self, config: Dict[str, Any], calib_data: Dict[str, Any]):
        """
        Initialize the camera
        
        Args:
            config: Configuration dictionary
            calib_data: Calibration data
            
        Raises:
            CameraError: If the camera cannot be initialized
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.calib_data = calib_data
        
        # Get camera configuration
        cam_config = config["cam"]
        self.sample_coords = cam_config["sample_coords"]
        self.sample_aperture = cam_config["sample_aperture"]
        self.warmup_frames = cam_config["warmup_frames"]
        self.flip_camera = cam_config["flip_camera"]
        self.flip_code = cam_config["flip_code"]
        
        try:
            self.vidcap = cv2.VideoCapture(cam_config["camera_deviceID"])
            
            if not self.vidcap.isOpened():
                raise CameraError("Failed to open camera")
                
            # Set camera properties from calibration data
            if "camera" in calib_data:
                for prop_name, prop_value in calib_data["camera"].items():
                    prop_id = getattr(cv2, prop_name)
                    self.vidcap.set(prop_id, prop_value)
                    
            # Warm up the camera
            for _ in range(self.warmup_frames):
                self.vidcap.read()
                
            self.logger.info("Camera initialized")
        except Exception as e:
            self.logger.error(f"Error initializing camera: {e}")
            raise CameraError(f"Failed to initialize camera: {e}")
            
    def close(self) -> None:
        """
        Release camera resources
        """
        if hasattr(self, 'vidcap') and self.vidcap is not None:
            self.vidcap.release()
            self.vidcap = None
            self.logger.debug("Camera resources released")
            
    def __del__(self) -> None:
        """
        Destructor to ensure camera resources are released
        """
        self.close()
        
    def get_frame(self) -> np.ndarray:
        """
        Get a frame from the camera
        
        Returns:
            Frame as a numpy array
            
        Raises:
            CameraError: If the frame cannot be captured
        """
        if self.vidcap is None:
            raise CameraError("Camera is not initialized")
            
        ret, frame = self.vidcap.read()
        
        if not ret:
            raise CameraError("Failed to capture frame")
            
        if self.flip_camera:
            frame = cv2.flip(frame, self.flip_code)
            
        return frame
        
    def get_faces(self, filename: Optional[str] = None) -> Tuple[List[str], List[str]]:
        """
        Get the colors of the visible faces
        
        Args:
            filename: Optional filename to save the captured image
            
        Returns:
            Tuple of two lists of colors (one for each row of faces)
            
        Raises:
            CameraError: If the faces cannot be detected
        """
        try:
            frame = self.get_frame()
            
            if filename:
                cv2.imwrite(filename, frame)
                
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            colors = []
            for coord in self.sample_coords:
                x, y = coord
                hsv_values = []
                
                # Sample a square area around the coordinate
                for i in range(-self.sample_aperture, self.sample_aperture + 1):
                    for j in range(-self.sample_aperture, self.sample_aperture + 1):
                        sample_x = x + i
                        sample_y = y + j
                        
                        if 0 <= sample_x < frame.shape[1] and 0 <= sample_y < frame.shape[0]:
                            hsv_values.append(hsv_frame[sample_y, sample_x])
                            
                # Calculate the average HSV value
                avg_hsv = np.mean(hsv_values, axis=0)
                color = guess_color(avg_hsv, self.calib_data["colors"])
                colors.append(color)
                
            # Split the colors into two rows
            row1 = colors[:3]
            row2 = colors[3:]
            
            return row1, row2
        except Exception as e:
            self.logger.error(f"Error getting faces: {e}")
            raise CameraError(f"Failed to get faces: {e}")
            
    def get_raw_hsv(self, filename: Optional[str] = None) -> Tuple[List[float], ...]:
        """
        Get the raw HSV values of the visible faces
        
        Args:
            filename: Optional filename to save the captured image
            
        Returns:
            Tuple of HSV values for each sample point
            
        Raises:
            CameraError: If the HSV values cannot be detected
        """
        try:
            frame = self.get_frame()
            
            if filename:
                cv2.imwrite(filename, frame)
                
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            hsv_values = []
            for coord in self.sample_coords:
                x, y = coord
                samples = []
                
                # Sample a square area around the coordinate
                for i in range(-self.sample_aperture, self.sample_aperture + 1):
                    for j in range(-self.sample_aperture, self.sample_aperture + 1):
                        sample_x = x + i
                        sample_y = y + j
                        
                        if 0 <= sample_x < frame.shape[1] and 0 <= sample_y < frame.shape[0]:
                            samples.append(hsv_frame[sample_y, sample_x])
                            
                # Calculate the average HSV value
                avg_hsv = np.mean(samples, axis=0).tolist()
                hsv_values.append(avg_hsv)
                
            return tuple(hsv_values)
        except Exception as e:
            self.logger.error(f"Error getting raw HSV values: {e}")
            raise CameraError(f"Failed to get raw HSV values: {e}")
            
    @staticmethod
    def get_settings() -> Dict[str, int]:
        """
        Get the current camera settings
        
        Returns:
            Dictionary of camera settings
        """
        settings = {}
        
        try:
            cap = cv2.VideoCapture(0)
            
            if cap.isOpened():
                for prop_id in [cv2.CAP_PROP_BRIGHTNESS, cv2.CAP_PROP_CONTRAST, 
                               cv2.CAP_PROP_SATURATION, cv2.CAP_PROP_HUE]:
                    prop_name = {
                        cv2.CAP_PROP_BRIGHTNESS: "CAP_PROP_BRIGHTNESS",
                        cv2.CAP_PROP_CONTRAST: "CAP_PROP_CONTRAST",
                        cv2.CAP_PROP_SATURATION: "CAP_PROP_SATURATION",
                        cv2.CAP_PROP_HUE: "CAP_PROP_HUE"
                    }.get(prop_id)
                    
                    if prop_name:
                        value = int(cap.get(prop_id))
                        settings[prop_name] = value
                        
                cap.release()
        except Exception as e:
            logging.error(f"Error getting camera settings: {e}")
            
        return settings
