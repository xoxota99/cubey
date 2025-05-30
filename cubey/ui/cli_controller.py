"""
Command-line interface controller for Cubey
"""

import logging
import sys
import time
from typing import Dict, Any, List, Optional, Callable

from cubey.exceptions import CubeyError
from cubey.hardware.motorcontroller import MotorController
from cubey.solver.scanner import Scanner
from cubey.solver.kociemba_solver import KociembaSolver
from cubey.solver.scrambler import Scrambler

class CLIController:
    """
    Controller for the command-line interface
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the CLI controller
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
    def solve(self, state: Optional[str] = None, interactive: bool = False) -> int:
        """
        Solve the cube
        
        Args:
            state: Optional cube state string (if not provided, will scan the cube)
            interactive: Whether to run in interactive mode
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        try:
            motors = MotorController(self.config)
            scanner = Scanner(self.config)
            solver = KociembaSolver(self.config)
            
            if interactive:
                return self._solve_interactive(scanner, solver, motors)
            else:
                return self._solve_automatic(scanner, solver, motors, state)
        except CubeyError as e:
            self.logger.error(f"Error: {e}")
            return 1
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return 1
            
    def _solve_automatic(self, scanner: Scanner, solver: KociembaSolver, 
                        motors: MotorController, state: Optional[str] = None) -> int:
        """
        Solve the cube automatically
        
        Args:
            scanner: Scanner instance
            solver: Solver instance
            motors: Motor controller instance
            state: Optional cube state string
            
        Returns:
            Exit code
        """
        self.logger.info("Solving cube automatically")
        
        # Get the cube state
        if state is None:
            self.logger.info("Scanning cube...")
            t0 = time.time()
            state = scanner.get_state_string(motors)
            t1 = time.time()
            
            if state is None:
                self.logger.error("Failed to get a valid cube state")
                return 1
                
            self.logger.info(f"Scanned state: {state}")
            self.logger.info(f"Scan time: {t1 - t0:.3f} seconds")
        else:
            self.logger.info(f"Using provided state: {state}")
            
        # Solve the cube
        self.logger.info("Solving...")
        t2 = time.time()
        solution = solver.solve(state)
        t3 = time.time()
        self.logger.info(f"Solution: {solution}")
        self.logger.info(f"Solve time: {t3 - t2:.3f} seconds")
        
        # Execute the solution
        self.logger.info("Executing solution...")
        t4 = time.time()
        motors.execute(solution)
        t5 = time.time()
        self.logger.info(f"Execution time: {t5 - t4:.3f} seconds")
        self.logger.info("Done!")
        
        return 0
        
    def _solve_interactive(self, scanner: Scanner, solver: KociembaSolver, 
                          motors: MotorController) -> int:
        """
        Solve the cube interactively
        
        Args:
            scanner: Scanner instance
            solver: Solver instance
            motors: Motor controller instance
            
        Returns:
            Exit code
        """
        self.logger.info("Solving cube interactively")
        
        # Scan the cube
        input("Press Enter to begin scanning the cube...")
        t0 = time.time()
        state = scanner.get_state_string(motors)
        t1 = time.time()
        
        if state is None:
            self.logger.error("Failed to get a valid cube state")
            return 1
            
        self.logger.info(f"Scan complete! Cube state: {state}")
        self.logger.info(f"Scan time: {t1 - t0:.3f} seconds")
        
        # Solve the cube
        input("Press Enter to generate the solution...")
        t2 = time.time()
        solution = solver.solve(state)
        t3 = time.time()
        self.logger.info(f"Solution found: {solution}")
        self.logger.info(f"Solve time: {t3 - t2:.3f} seconds")
        
        # Execute the solution
        input("Press Enter to execute the solution...")
        t4 = time.time()
        motors.execute(solution)
        t5 = time.time()
        self.logger.info(f"Execution time: {t5 - t4:.3f} seconds")
        self.logger.info("Done!")
        
        return 0
        
    def scramble(self, moves: Optional[int] = None) -> int:
        """
        Scramble the cube
        
        Args:
            moves: Number of moves for scrambling
            
        Returns:
            Exit code
        """
        try:
            motors = MotorController(self.config)
            scrambler = Scrambler(self.config)
            
            scramble = scrambler.scramble(moves)
            self.logger.info(f"Scramble: {scramble}")
            
            self.logger.info("Executing scramble...")
            motors.execute(scramble)
            self.logger.info("Done!")
            
            return 0
        except CubeyError as e:
            self.logger.error(f"Error: {e}")
            return 1
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return 1
            
    def scan(self, output_file: Optional[str] = None) -> int:
        """
        Scan the cube
        
        Args:
            output_file: Optional file to write the state to
            
        Returns:
            Exit code
        """
        try:
            motors = MotorController(self.config)
            scanner = Scanner(self.config)
            
            self.logger.info("Scanning cube...")
            state = scanner.get_state_string(motors)
            
            if state is None:
                self.logger.error("Failed to get a valid cube state")
                return 1
                
            self.logger.info(f"Cube state: {state}")
            
            if output_file:
                with open(output_file, "w") as f:
                    f.write(state)
                self.logger.info(f"State written to {output_file}")
                
            return 0
        except CubeyError as e:
            self.logger.error(f"Error: {e}")
            return 1
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return 1
            
    def manual(self, moves: Optional[str] = None) -> int:
        """
        Manual control of the cube
        
        Args:
            moves: Optional moves to execute
            
        Returns:
            Exit code
        """
        try:
            motors = MotorController(self.config)
            
            if moves:
                self.logger.info(f"Executing moves: {moves}")
                motors.execute(moves)
                self.logger.info("Done!")
            else:
                self.logger.info("Enter moves (e.g., 'F R U R\\' U\\' F\\'). Type 'quit' to exit.")
                while True:
                    try:
                        moves = input("> ")
                        if moves.lower() in ("quit", "exit", "q"):
                            break
                        motors.execute(moves)
                    except CubeyError as e:
                        self.logger.error(f"Error: {e}")
                    except Exception as e:
                        self.logger.error(f"Unexpected error: {e}")
                        
            return 0
        except CubeyError as e:
            self.logger.error(f"Error: {e}")
            return 1
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return 1
