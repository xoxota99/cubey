import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cubey.hardware.motorcontroller import MotorController

class TestMotorController(unittest.TestCase):
    """Test cases for the MotorController class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock config
        self.config = {
            'stepper': {
                'pin_map': {
                    'up': 1,
                    'right': 2,
                    'front': 3,
                    'down': 4,
                    'left': 5,
                    'back': 6,
                    'dir': 7,
                    'disable': 8
                },
                'steps_per_rev': 200,
                'move_delay': 0.01,
                'hertz': 2000,
                'step_factor': 8
            }
        }
        
    @patch('lib.motorcontroller.pigpio')
    def test_initialization(self, mock_pigpio):
        """Test that the MotorController initializes correctly"""
        # Create a mock for the pigpio.pi() function
        mock_pi = MagicMock()
        mock_pigpio.pi.return_value = mock_pi
        
        # Create a MotorController instance
        motor_controller = MotorController(self.config)
        
        # Check that the global variables were set correctly
        self.assertEqual(motor_controller._MotorController__dir_pin, 7)
        self.assertEqual(motor_controller._MotorController__disable_pin, 8)
        self.assertEqual(motor_controller._MotorController__face_motor_map['U'], 1)
        self.assertEqual(motor_controller._MotorController__face_motor_map['R'], 2)
        self.assertEqual(motor_controller._MotorController__face_motor_map['F'], 3)
        self.assertEqual(motor_controller._MotorController__face_motor_map['D'], 4)
        self.assertEqual(motor_controller._MotorController__face_motor_map['L'], 5)
        self.assertEqual(motor_controller._MotorController__face_motor_map['B'], 6)
        
    @patch('lib.motorcontroller.pigpio')
    def test_execute_valid_recipe(self, mock_pigpio):
        """Test execute with a valid recipe"""
        # Create a mock for the pigpio.pi() function
        mock_pi = MagicMock()
        mock_pigpio.pi.return_value = mock_pi
        
        # Create a MotorController instance
        motor_controller = MotorController(self.config)
        
        # Mock the _initialize method
        motor_controller._initialize = MagicMock()
        
        # Mock the rot_90 and rot_180 methods
        motor_controller.rot_90 = MagicMock()
        motor_controller.rot_180 = MagicMock()
        
        # Mock the _stop method
        motor_controller._stop = MagicMock()
        
        # Execute a valid recipe
        result = motor_controller.execute("R L2 F B U' F' D")
        
        # Check that the methods were called correctly
        self.assertEqual(motor_controller.rot_90.call_count, 5)
        self.assertEqual(motor_controller.rot_180.call_count, 1)
        self.assertEqual(motor_controller._stop.call_count, 1)
        self.assertTrue(result)
        
    @patch('lib.motorcontroller.pigpio')
    def test_execute_invalid_recipe(self, mock_pigpio):
        """Test execute with an invalid recipe"""
        # Create a mock for the pigpio.pi() function
        mock_pi = MagicMock()
        mock_pigpio.pi.return_value = mock_pi
        
        # Create a MotorController instance
        motor_controller = MotorController(self.config)
        
        # Mock the _initialize method
        motor_controller._initialize = MagicMock()
        
        # Mock the rot_90 and rot_180 methods
        motor_controller.rot_90 = MagicMock()
        motor_controller.rot_180 = MagicMock()
        
        # Mock the _stop method
        motor_controller._stop = MagicMock()
        
        # Execute an invalid recipe
        result = motor_controller.execute("R L2 X B U' F' D")  # 'X' is not a valid face
        
        # Check that the methods were not called
        self.assertEqual(motor_controller.rot_90.call_count, 0)
        self.assertEqual(motor_controller.rot_180.call_count, 0)
        self.assertEqual(motor_controller._stop.call_count, 0)
        self.assertFalse(result)
        
    @patch('lib.motorcontroller.pigpio')
    def test_rot_90(self, mock_pigpio):
        """Test rot_90 method"""
        # Create a mock for the pigpio.pi() function
        mock_pi = MagicMock()
        mock_pigpio.pi.return_value = mock_pi
        
        # Create a MotorController instance
        motor_controller = MotorController(self.config)
        
        # Mock the _initialize and _tx_pulses methods
        motor_controller._initialize = MagicMock()
        motor_controller._tx_pulses = MagicMock()
        
        # Call rot_90
        motor_controller.rot_90(1, 1)
        
        # Check that the methods were called correctly
        motor_controller._initialize.assert_called_once()
        motor_controller._tx_pulses.assert_called_once()
        
    @patch('lib.motorcontroller.pigpio')
    def test_rot_180(self, mock_pigpio):
        """Test rot_180 method"""
        # Create a mock for the pigpio.pi() function
        mock_pi = MagicMock()
        mock_pigpio.pi.return_value = mock_pi
        
        # Create a MotorController instance
        motor_controller = MotorController(self.config)
        
        # Mock the _initialize and _tx_pulses methods
        motor_controller._initialize = MagicMock()
        motor_controller._tx_pulses = MagicMock()
        
        # Call rot_180
        motor_controller.rot_180(1, 1)
        
        # Check that the methods were called correctly
        motor_controller._initialize.assert_called_once()
        motor_controller._tx_pulses.assert_called_once()

if __name__ == '__main__':
    unittest.main()
