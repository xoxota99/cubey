import unittest
import sys
import os
import yaml
from unittest.mock import MagicMock, patch

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cubey.solver.scanner import Scanner

class TestScanner(unittest.TestCase):
    """Test cases for the Scanner class and related functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock config
        self.config = {
            'cam': {
                'calibration': 'default_calib.yaml',
                'sample_coords': [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                'warmup_frames': 1,
                'camera_deviceID': 0,
                'sample_aperture': 10,
                'flip_camera': False,
                'flip_code': 1
            }
        }
        
    @patch('lib.scanner.Camera')
    def test_scanner_initialization(self, mock_camera):
        """Test that the Scanner initializes correctly"""
        # Create a mock for the Camera class
        mock_camera_instance = MagicMock()
        mock_camera.return_value = mock_camera_instance
        
        # Create a Scanner instance
        scanner = Scanner(self.config)
        
        # Check that the Camera was initialized with the correct parameters
        mock_camera.assert_called_once()
        
    def test_get_state_from_string(self):
        """Test the get_state_from_string function"""
        # Create a solved cube state string (all faces with their respective colors)
        solved_state_str = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
        
        # Convert to state dictionary
        state_dict = get_state_from_string(solved_state_str)
        
        # Check that each face has the correct colors
        self.assertEqual(state_dict['U'], ['U', 'U', 'U', 'U', 'U', 'U', 'U', 'U', 'U'])
        self.assertEqual(state_dict['R'], ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'])
        self.assertEqual(state_dict['F'], ['F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F'])
        self.assertEqual(state_dict['D'], ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D'])
        self.assertEqual(state_dict['L'], ['L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L'])
        self.assertEqual(state_dict['B'], ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'])
        
    @patch('lib.scanner.Scanner.scan_state')
    def test_get_state_string_valid(self, mock_scan_state):
        """Test get_state_string with a valid state"""
        # Create a mock for the scan_state method
        mock_scan_state.return_value = {
            'U': ['U', 'U', 'U', 'U', 'U', 'U', 'U', 'U', 'U'],
            'R': ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
            'F': ['F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F'],
            'D': ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D'],
            'L': ['L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L'],
            'B': ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B']
        }
        
        # Create a Scanner instance with mocked Camera
        with patch('lib.scanner.Camera'):
            scanner = Scanner(self.config)
            
            # Get the state string
            state_str = scanner.get_state_string(None)
            
            # Check that the state string is correct
            self.assertEqual(state_str, "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")
            
    @patch('lib.scanner.Scanner.scan_state')
    def test_get_state_string_invalid_length(self, mock_scan_state):
        """Test get_state_string with an invalid state (wrong length)"""
        # Create a mock for the scan_state method with an invalid state
        mock_scan_state.return_value = {
            'U': ['U', 'U', 'U', 'U', 'U', 'U', 'U', 'U'],  # Missing one facelet
            'R': ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
            'F': ['F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F'],
            'D': ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D'],
            'L': ['L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L'],
            'B': ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B']
        }
        
        # Create a Scanner instance with mocked Camera
        with patch('lib.scanner.Camera'):
            scanner = Scanner(self.config)
            
            # Get the state string
            state_str = scanner.get_state_string(None)
            
            # Check that the state string is None
            self.assertIsNone(state_str)
            
    @patch('lib.scanner.Scanner.scan_state')
    def test_get_state_string_invalid_centers(self, mock_scan_state):
        """Test get_state_string with an invalid state (wrong center facelets)"""
        # Create a mock for the scan_state method with an invalid state
        mock_scan_state.return_value = {
            'U': ['U', 'U', 'U', 'U', 'R', 'U', 'U', 'U', 'U'],  # Wrong center
            'R': ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
            'F': ['F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F'],
            'D': ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D'],
            'L': ['L', 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L'],
            'B': ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B']
        }
        
        # Create a Scanner instance with mocked Camera
        with patch('lib.scanner.Camera'):
            scanner = Scanner(self.config)
            
            # Get the state string
            state_str = scanner.get_state_string(None)
            
            # Check that the state string is None
            self.assertIsNone(state_str)

if __name__ == '__main__':
    unittest.main()
