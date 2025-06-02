"""
Integration module for the web interface with the main Cubey functionality.

This module provides the integration between the web interface and the core
Cubey functionality, including the scanner, solver, and motor controller.
"""

import logging
from typing import Dict, Any, Optional, Callable, List, Tuple

from flask import Flask, request, jsonify, Response

from cubey.solver.scanner import Scanner
from cubey.solver.kociemba_solver import KociembaSolver
from cubey.hardware.motorcontroller import MotorController
from cubey.solver.scrambler import scramble_cube


class CubeyWebIntegration:
    """
    Integration class for the web interface with the main Cubey functionality.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the integration.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize components
        self.scanner = Scanner(config)
        self.solver = KociembaSolver(config)
        self.motors = MotorController(config)
        
        self.logger.info("Web integration initialized")
        
    def scan_cube(self) -> Dict[str, Any]:
        """
        Scan the cube and return the state.
        
        Returns:
            Dictionary with scan results
        """
        self.logger.info("Scanning cube")
        
        try:
            state = self.scanner.get_state_string(self.motors)
            
            if state is None:
                return {"success": False, "error": "Failed to get a valid cube state"}
                
            return {"success": True, "state": state}
        except Exception as e:
            self.logger.error(f"Error scanning cube: {e}")
            return {"success": False, "error": str(e)}
            
    def solve_cube(self, state: Optional[str] = None) -> Dict[str, Any]:
        """
        Solve the cube and execute the solution.
        
        Args:
            state: Optional cube state (if None, will scan the cube)
            
        Returns:
            Dictionary with solve results
        """
        self.logger.info("Solving cube")
        
        try:
            # Get the cube state if not provided
            if state is None:
                scan_result = self.scan_cube()
                
                if not scan_result["success"]:
                    return scan_result
                    
                state = scan_result["state"]
                
            # Solve the cube
            solution = self.solver.solve(state)
            
            # Execute the solution
            self.motors.execute(solution)
            
            return {"success": True, "solution": solution}
        except Exception as e:
            self.logger.error(f"Error solving cube: {e}")
            return {"success": False, "error": str(e)}
            
    def scramble_cube(self, moves: Optional[int] = None) -> Dict[str, Any]:
        """
        Scramble the cube.
        
        Args:
            moves: Optional number of moves
            
        Returns:
            Dictionary with scramble results
        """
        self.logger.info("Scrambling cube")
        
        try:
            scramble = scramble_cube(self.config, self.motors, moves)
            return {"success": True, "scramble": scramble}
        except Exception as e:
            self.logger.error(f"Error scrambling cube: {e}")
            return {"success": False, "error": str(e)}
            
    def execute_moves(self, moves: str) -> Dict[str, Any]:
        """
        Execute a sequence of moves.
        
        Args:
            moves: Moves to execute
            
        Returns:
            Dictionary with execution results
        """
        self.logger.info(f"Executing moves: {moves}")
        
        try:
            self.motors.execute(moves)
            return {"success": True}
        except Exception as e:
            self.logger.error(f"Error executing moves: {e}")
            return {"success": False, "error": str(e)}


def create_api_routes(app: Flask, integration: CubeyWebIntegration) -> None:
    """
    Create API routes for the web interface.
    
    Args:
        app: Flask application
        integration: CubeyWebIntegration instance
    """
    
    @app.route('/api/scan', methods=['POST'])
    def api_scan() -> Response:
        """
        API endpoint for scanning the cube.
        
        Returns:
            JSON response
        """
        result = integration.scan_cube()
        return jsonify(result)
        
    @app.route('/api/solve', methods=['POST'])
    def api_solve() -> Response:
        """
        API endpoint for solving the cube.
        
        Returns:
            JSON response
        """
        data = request.get_json() or {}
        state = data.get('state')
        result = integration.solve_cube(state)
        return jsonify(result)
        
    @app.route('/api/scramble', methods=['POST'])
    def api_scramble() -> Response:
        """
        API endpoint for scrambling the cube.
        
        Returns:
            JSON response
        """
        data = request.get_json() or {}
        moves = data.get('moves')
        result = integration.scramble_cube(moves)
        return jsonify(result)
        
    @app.route('/api/execute', methods=['POST'])
    def api_execute() -> Response:
        """
        API endpoint for executing moves.
        
        Returns:
            JSON response
        """
        data = request.get_json() or {}
        moves = data.get('moves')
        
        if not moves:
            return jsonify({"success": False, "error": "No moves provided"})
            
        result = integration.execute_moves(moves)
        return jsonify(result)
