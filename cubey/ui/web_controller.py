"""
Web interface controller for Cubey
"""

import logging
import os
import time
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify

from cubey.exceptions import CubeyError
from cubey.hardware.motorcontroller import MotorController
from cubey.solver.scanner import Scanner
from cubey.solver.kociemba_solver import KociembaSolver
from cubey.solver.scrambler import Scrambler
from cubey.config import get_merged_config

class WebController:
    """
    Controller for the web interface
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the web controller
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.status = {
            'state': 'idle',
            'last_scan': None,
            'last_solution': None,
            'error': None
        }
        
    def create_app(self) -> Flask:
        """
        Create the Flask application
        
        Returns:
            Flask application
        """
        app = Flask(__name__, 
                   template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                   static_folder=os.path.join(os.path.dirname(__file__), 'static'))
        
        # Configure CSRF protection
        from flask_wtf.csrf import CSRFProtect
        csrf = CSRFProtect(app)
        app.config['SECRET_KEY'] = os.urandom(24)
        
        # Register routes
        @app.route('/')
        def index():
            return render_template('index.html')
            
        @app.route('/api/status')
        def get_status():
            return jsonify(self.get_status())
            
        @app.route('/api/scan', methods=['POST'])
        def scan_cube():
            return jsonify(self.scan_cube())
            
        @app.route('/api/solve', methods=['POST'])
        def solve_cube():
            return jsonify(self.solve_cube())
            
        @app.route('/api/scramble', methods=['POST'])
        def scramble_cube():
            moves = request.json.get('moves', 20) if request.json else 20
            return jsonify(self.scramble_cube(moves))
            
        @app.route('/api/move', methods=['POST'])
        def execute_move():
            move = request.json.get('move', '') if request.json else ''
            return jsonify(self.execute_move(move))
            
        return app
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status
        
        Returns:
            Status dictionary
        """
        return self.status
        
    def scan_cube(self) -> Dict[str, Any]:
        """
        Scan the cube
        
        Returns:
            Result dictionary
        """
        self.status['state'] = 'scanning'
        self.status['error'] = None
        
        try:
            motors = MotorController(self.config)
            scanner = Scanner(self.config)
            
            state = scanner.get_state_string(motors)
            
            if state is None:
                self.status['state'] = 'error'
                self.status['error'] = 'Failed to get a valid cube state'
                return {'success': False, 'error': 'Failed to get a valid cube state'}
                
            self.status['last_scan'] = state
            self.status['state'] = 'idle'
            
            return {'success': True, 'state': state}
        except Exception as e:
            self.logger.error(f"Error scanning cube: {e}")
            self.status['state'] = 'error'
            self.status['error'] = str(e)
            return {'success': False, 'error': str(e)}
            
    def solve_cube(self) -> Dict[str, Any]:
        """
        Solve the cube
        
        Returns:
            Result dictionary
        """
        if not self.status['last_scan']:
            return {'success': False, 'error': 'No scan available. Please scan the cube first.'}
            
        self.status['state'] = 'solving'
        self.status['error'] = None
        
        try:
            motors = MotorController(self.config)
            solver = KociembaSolver(self.config)
            
            solution = solver.solve(self.status['last_scan'])
            self.status['last_solution'] = solution
            
            self.status['state'] = 'executing'
            motors.execute(solution)
            self.status['state'] = 'idle'
            
            return {'success': True, 'solution': solution}
        except Exception as e:
            self.logger.error(f"Error solving cube: {e}")
            self.status['state'] = 'error'
            self.status['error'] = str(e)
            return {'success': False, 'error': str(e)}
            
    def scramble_cube(self, moves: int = 20) -> Dict[str, Any]:
        """
        Scramble the cube
        
        Args:
            moves: Number of moves for scrambling
            
        Returns:
            Result dictionary
        """
        self.status['state'] = 'scrambling'
        self.status['error'] = None
        
        try:
            motors = MotorController(self.config)
            scrambler = Scrambler(self.config)
            
            scramble = scrambler.scramble(moves)
            
            motors.execute(scramble)
            self.status['state'] = 'idle'
            
            return {'success': True, 'scramble': scramble}
        except Exception as e:
            self.logger.error(f"Error scrambling cube: {e}")
            self.status['state'] = 'error'
            self.status['error'] = str(e)
            return {'success': False, 'error': str(e)}
            
    def execute_move(self, move: str) -> Dict[str, Any]:
        """
        Execute a single move or sequence
        
        Args:
            move: Move or sequence to execute
            
        Returns:
            Result dictionary
        """
        if not move:
            return {'success': False, 'error': 'No move specified'}
            
        self.status['state'] = 'executing'
        self.status['error'] = None
        
        try:
            motors = MotorController(self.config)
            motors.execute(move)
            self.status['state'] = 'idle'
            
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error executing move: {e}")
            self.status['state'] = 'error'
            self.status['error'] = str(e)
            return {'success': False, 'error': str(e)}
            
def create_app(config_path: Optional[str] = None) -> Flask:
    """
    Create the Flask application
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Flask application
    """
    config = get_merged_config(config_path)
    controller = WebController(config)
    return controller.create_app()
    
def main(host: str = '0.0.0.0', port: int = 5000, config_path: Optional[str] = None) -> None:
    """
    Run the web server
    
    Args:
        host: Host to bind to
        port: Port to bind to
        config_path: Path to configuration file
    """
    app = create_app(config_path)
    app.run(host=host, port=port, debug=True)
