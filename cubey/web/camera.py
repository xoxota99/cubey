"""
Camera module for the web interface.

This module provides a camera class for capturing and streaming video frames
for the web interface.
"""

import time
import threading
from typing import Optional, Dict, Any, List, Callable

import cv2
import numpy as np

from cubey.config.loader import get_merged_config
from cubey.web.frame_event import FrameEvent


class Camera:
    """
    Camera class for capturing and streaming video frames.
    """
    
    def __init__(self, camera_id: Optional[int] = None):
        """
        Initialize the camera.
        
        Args:
            camera_id: Camera device ID (if None, uses the one from config)
        """
        # Load configuration
        self.config = get_merged_config()
        cam_config = self.config["cam"]
        
        # Set camera parameters
        self.camera_id = camera_id if camera_id is not None else cam_config["camera_deviceID"]
        self.frame_width = cam_config.get("frame_width", 640)
        self.frame_height = cam_config.get("frame_height", 480)
        self.flip_camera = cam_config.get("flip_camera", False)
        self.flip_code = cam_config.get("flip_code", 0)
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        
        # Initialize frame event
        self.frame_event = FrameEvent()
        
        # Initialize threading
        self.thread = threading.Thread(target=self._thread_function)
        self.thread.daemon = True
        self.running = True
        self.thread.start()
        
        # Wait for camera to initialize
        time.sleep(0.5)
        
    def _thread_function(self) -> None:
        """
        Thread function for capturing frames.
        """
        while self.running:
            success, frame = self.cap.read()
            
            if success:
                # Flip the frame if needed
                if self.flip_camera:
                    frame = cv2.flip(frame, self.flip_code)
                
                # Encode the frame as JPEG
                _, jpeg = cv2.imencode('.jpg', frame)
                
                # Notify listeners
                self.frame_event.on_new_frame(jpeg.tobytes())
            
            # Sleep to control frame rate
            time.sleep(0.03)  # ~30 FPS
            
    def get_frame(self) -> Optional[bytes]:
        """
        Get the latest frame.
        
        Returns:
            JPEG encoded frame or None if no frame is available
        """
        return self.frame_event.get_latest_frame()
        
    def add_frame_listener(self, callback: Callable[[bytes], None]) -> None:
        """
        Add a listener for new frames.
        
        Args:
            callback: Function to call when a new frame is available
        """
        self.frame_event.add_listener(callback)
        
    def remove_frame_listener(self, callback: Callable[[bytes], None]) -> None:
        """
        Remove a frame listener.
        
        Args:
            callback: Function to remove
        """
        self.frame_event.remove_listener(callback)
        
    def stop(self) -> None:
        """
        Stop the camera and release resources.
        """
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.cap.release()
