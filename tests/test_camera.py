"""
Tests for the Camera class
"""

import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import os
import sys

from cubey.hardware.camera import Camera, test_color, guess_color


class TestCamera(unittest.TestCase):
    """Test cases for the Camera class"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'cam': {
                'camera_deviceID': 0,
                'sample_coords': [[100, 100], [200, 200], [300, 300], [400, 400], [500, 500], [600, 600]],
                'sample_aperture': 5,
                'warmup_frames': 2,
                'flip_camera': False,
                'flip_code': 0
            }
        }
        
        self.calib_data = {
            'camera': {
                'CAP_PROP_BRIGHTNESS': 50,
                'CAP_PROP_CONTRAST': 50
            },
            'colors': {
                'U': {
                    'min': np.array([0, 0, 200]),
                    'max': np.array([180, 30, 255])
                },
                'R': {
                    'min': np.array([160, 100, 100]),
                    'max': np.array([10, 255, 255])
                }
            }
        }

    @patch('cubey.core.camera.cv2.VideoCapture')
    def test_camera_init(self, mock_video_capture):
        """Test Camera initialization"""
        # Setup mock
        mock_instance = MagicMock()
        mock_video_capture.return_value = mock_instance
        
        # Create camera
        camera = Camera(self.config, self.calib_data)
        
        # Verify
        mock_video_capture.assert_called_once_with(0)
        self.assertEqual(camera.sample_coords, self.config['cam']['sample_coords'])
        
    @patch('cubey.core.camera.cv2.VideoCapture')
    def test_camera_close(self, mock_video_capture):
        """Test Camera close method"""
        # Setup mock
        mock_instance = MagicMock()
        mock_video_capture.return_value = mock_instance
        
        # Create and close camera
        camera = Camera(self.config, self.calib_data)
        camera.close()
        
        # Verify
        mock_instance.release.assert_called_once()
        self.assertIsNone(camera.vidcap)
        
    def test_test_color(self):
        """Test the test_color function"""
        # Normal case
        self.assertTrue(test_color(
            np.array([100, 150, 200]),
            np.array([50, 100, 150]),
            np.array([150, 200, 250])
        ))
        
        # Edge case - outside range
        self.assertFalse(test_color(
            np.array([200, 150, 200]),
            np.array([50, 100, 150]),
            np.array([150, 200, 250])
        ))
        
        # Special case - red color wrapping around hue
        self.assertTrue(test_color(
            np.array([5, 150, 200]),
            np.array([160, 100, 150]),
            np.array([10, 200, 250])
        ))
        
    def test_guess_color(self):
        """Test the guess_color function"""
        # White color
        self.assertEqual(
            guess_color(np.array([90, 10, 240]), self.calib_data['colors']),
            'U'
        )
        
        # Red color
        self.assertEqual(
            guess_color(np.array([5, 200, 200]), self.calib_data['colors']),
            'R'
        )
        
        # Unknown color
        self.assertEqual(
            guess_color(np.array([90, 90, 90]), self.calib_data['colors']),
            'X'
        )


if __name__ == '__main__':
    unittest.main()
