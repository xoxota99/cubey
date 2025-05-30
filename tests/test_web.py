"""
Tests for the web interface
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

from cubey.web.integration import CubeyWebIntegration


class TestWebIntegration(unittest.TestCase):
    """Test cases for the web integration"""

    @patch('cubey.web.integration.Scanner')
    @patch('cubey.web.integration.MotorController')
    def setUp(self, mock_motor_controller, mock_scanner):
        """Set up test fixtures"""
        # Mock config
        self.config = {
            'cam': {
                'camera_deviceID': 0,
                'sample_coords': [[100, 100]],
                'sample_aperture': 5,
                'warmup_frames': 2,
                'flip_camera': False,
                'flip_code': 0,
                'calibration': 'default_calib.yaml'
            },
            'motor': {
                'speed': 100,
                'pins': {
                    'U': 1,
                    'R': 2,
                    'F': 3,
                    'D': 4,
                    'L': 5,
                    'B': 6
                }
            }
        }
        
        # Mock scanner and motor controller
        self.mock_scanner = mock_scanner.return_value
        self.mock_motors = mock_motor_controller.return_value
        
        # Create integration with mocked dependencies
        with patch('yaml.load', return_value=self.config):
            with patch('builtins.open', MagicMock()):
                self.integration = CubeyWebIntegration('dummy_path')
                
        # Replace dependencies with mocks
        self.integration.scanner = self.mock_scanner
        self.integration.motors = self.mock_motors

    def test_get_status(self):
        """Test get_status method"""
        # Initial status should be idle
        status = self.integration.get_status()
        self.assertEqual(status['state'], 'idle')
        self.assertIsNone(status['last_scan'])
        self.assertIsNone(status['last_solution'])
        self.assertIsNone(status['error'])
        
    def test_scan_cube_success(self):
        """Test scan_cube method with successful scan"""
        # Mock scanner to return a valid state
        self.mock_scanner.get_state_string.return_value = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
        
        # Call scan_cube
        result = self.integration.scan_cube()
        
        # Verify
        self.assertTrue(result['success'])
        self.assertEqual(result['state'], "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")
        self.assertEqual(self.integration.status['last_scan'], "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")
        self.assertEqual(self.integration.status['state'], 'idle')
        
    def test_scan_cube_failure(self):
        """Test scan_cube method with failed scan"""
        # Mock scanner to return None (invalid state)
        self.mock_scanner.get_state_string.return_value = None
        
        # Call scan_cube
        result = self.integration.scan_cube()
        
        # Verify
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(self.integration.status['state'], 'error')
        
    @patch('cubey.kociemba.solve')
    def test_solve_cube_success(self, mock_solve):
        """Test solve_cube method with successful solve"""
        # Set up a previous scan
        self.integration.status['last_scan'] = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
        
        # Mock solver to return a solution
        mock_solve.return_value = "F R U R' U' F'"
        
        # Call solve_cube
        result = self.integration.solve_cube()
        
        # Verify
        self.assertTrue(result['success'])
        self.assertEqual(result['solution'], "F R U R' U' F'")
        self.assertEqual(self.integration.status['last_solution'], "F R U R' U' F'")
        self.assertEqual(self.integration.status['state'], 'idle')
        self.mock_motors.execute.assert_called_once_with("F R U R' U' F'")
        
    def test_solve_cube_no_scan(self):
        """Test solve_cube method with no previous scan"""
        # Ensure no previous scan
        self.integration.status['last_scan'] = None
        
        # Call solve_cube
        result = self.integration.solve_cube()
        
        # Verify
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('scan', result['error'])
        
    def test_execute_move_success(self):
        """Test execute_move method with successful execution"""
        # Call execute_move
        result = self.integration.execute_move("F")
        
        # Verify
        self.assertTrue(result['success'])
        self.assertEqual(self.integration.status['state'], 'idle')
        self.mock_motors.execute.assert_called_once_with("F")
        
    def test_execute_move_failure(self):
        """Test execute_move method with failed execution"""
        # Mock motors to raise an exception
        self.mock_motors.execute.side_effect = Exception("Invalid move")
        
        # Call execute_move
        result = self.integration.execute_move("X")  # Invalid move
        
        # Verify
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(self.integration.status['state'], 'error')


if __name__ == '__main__':
    unittest.main()
