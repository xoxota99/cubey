import os
import sys
import yaml
import logging
from typing import Dict, Any, Optional
from flask import Flask, render_template, Response, request, jsonify
import threading
import json

# Add parent directory to path so we can import the main modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cubey.solver.scanner import Scanner
from cubey.hardware.motorcontroller import MotorController
from cubey.utils.logging_config import setup_logging
import kociemba

"""
Integration module for the web interface with the main cubey functionality
"""

class CubeyWebIntegration:
    """
    Class to integrate the web interface with the main cubey functionality
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the integration with the given configuration
        
        Args:
            config_path: Path to the configuration file
        """
        # Load configuration
        with open(config_path, 'r') as ymlfile:
            self.config = yaml.load(ymlfile, Loader=yaml.FullLoader)
            
        # Set up logging
        setup_logging(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.scanner = Scanner(self.config)
        self.motors = MotorController(self.config)
        
        # Status tracking
        self.status = {
            "state": "idle",
            "last_scan": None,
            "last_solution": None,
            "error": None
        }
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the system
        
        Returns:
            Dictionary with the current status
        """
        with self.lock:
            return dict(self.status)
            
    def scan_cube(self) -> Dict[str, Any]:
        """
        Scan the cube and return the state
        
        Returns:
            Dictionary with the scan result
        """
        with self.lock:
            self.status["state"] = "scanning"
            self.status["error"] = None
            
        try:
            state_str = self.scanner.get_state_string(self.motors)
            
            with self.lock:
                if state_str is None:
                    self.status["error"] = "Failed to get a valid cube state"
                    self.status["state"] = "error"
                    return {"success": False, "error": self.status["error"]}
                    
                self.status["last_scan"] = state_str
                self.status["state"] = "idle"
                return {"success": True, "state": state_str}
                
        except Exception as e:
            error_msg = f"Error scanning cube: {str(e)}"
            self.logger.error(error_msg)
            
            with self.lock:
                self.status["error"] = error_msg
                self.status["state"] = "error"
                return {"success": False, "error": error_msg}
    
    def solve_cube(self) -> Dict[str, Any]:
        """
        Solve the cube using the last scan
        
        Returns:
            Dictionary with the solve result
        """
        with self.lock:
            if self.status["last_scan"] is None:
                return {"success": False, "error": "No scan available. Please scan the cube first."}
                
            self.status["state"] = "solving"
            self.status["error"] = None
            last_scan = self.status["last_scan"]
            
        try:
            # Get solution
            solution = kociemba.solve(last_scan)
            
            with self.lock:
                self.status["last_solution"] = solution
                self.status["state"] = "executing"
                
            # Execute solution
            self.motors.execute(solution)
            
            with self.lock:
                self.status["state"] = "idle"
                return {"success": True, "solution": solution}
                
        except Exception as e:
            error_msg = f"Error solving cube: {str(e)}"
            self.logger.error(error_msg)
            
            with self.lock:
                self.status["error"] = error_msg
                self.status["state"] = "error"
                return {"success": False, "error": error_msg}
    
    def execute_move(self, move: str) -> Dict[str, Any]:
        """
        Execute a single move or sequence
        
        Args:
            move: Move or sequence to execute
            
        Returns:
            Dictionary with the execution result
        """
        with self.lock:
            self.status["state"] = "executing"
            self.status["error"] = None
            
        try:
            result = self.motors.execute(move)
            
            with self.lock:
                self.status["state"] = "idle"
                return {"success": result}
                
        except Exception as e:
            error_msg = f"Error executing move: {str(e)}"
            self.logger.error(error_msg)
            
            with self.lock:
                self.status["error"] = error_msg
                self.status["state"] = "error"
                return {"success": False, "error": error_msg}

# Create Flask routes for the integration
def create_api_routes(app: Flask, integration: CubeyWebIntegration) -> None:
    """
    Create API routes for the integration
    
    Args:
        app: Flask application
        integration: CubeyWebIntegration instance
    """
    @app.route('/api/status')
    def api_status():
        """Get the current status of the system"""
        return jsonify(integration.get_status())
        
    @app.route('/api/scan', methods=['POST'])
    def api_scan():
        """Scan the cube"""
        return jsonify(integration.scan_cube())
        
    @app.route('/api/solve', methods=['POST'])
    def api_solve():
        """Solve the cube"""
        return jsonify(integration.solve_cube())
        
    @app.route('/api/move', methods=['POST'])
    def api_move():
        """Execute a move"""
        data = request.get_json()
        if not data or 'move' not in data:
            return jsonify({"success": False, "error": "Missing 'move' parameter"}), 400
            
        return jsonify(integration.execute_move(data['move']))
