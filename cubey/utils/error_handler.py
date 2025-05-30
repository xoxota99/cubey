"""
Global error handling utilities for Cubey
"""

import sys
import traceback
import logging
from typing import Callable, Any, TypeVar, cast

from cubey.exceptions import CubeyError

# Type variable for generic function
F = TypeVar('F', bound=Callable[..., Any])

logger = logging.getLogger(__name__)


def handle_errors(exit_on_error: bool = False) -> Callable[[F], F]:
    """
    Decorator for handling errors in functions
    
    Args:
        exit_on_error: Whether to exit the program on error
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except CubeyError as e:
                logger.error(f"{e.__class__.__name__}: {str(e)}")
                if exit_on_error:
                    sys.exit(1)
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                logger.debug(traceback.format_exc())
                if exit_on_error:
                    sys.exit(1)
            return None
        return cast(F, wrapper)
    return decorator


def setup_global_exception_handler() -> None:
    """
    Set up a global exception handler for unhandled exceptions
    """
    def global_exception_handler(exctype: Any, value: Any, tb: Any) -> None:
        logger.critical(f"Unhandled {exctype.__name__}: {value}")
        logger.debug(''.join(traceback.format_tb(tb)))
        sys.__excepthook__(exctype, value, tb)
    
    sys.excepthook = global_exception_handler
