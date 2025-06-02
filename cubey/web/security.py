"""
Security utilities for the web interface
"""

import secrets
from typing import Dict, Any, Callable
from functools import wraps
from flask import request, Response, current_app

def generate_csrf_token() -> str:
    """
    Generate a CSRF token
    
    Returns:
        CSRF token
    """
    return secrets.token_hex(16)

def validate_csrf_token(token: str) -> bool:
    """
    Validate a CSRF token
    
    Args:
        token: CSRF token to validate
        
    Returns:
        True if the token is valid, False otherwise
    """
    if not token or not current_app.config.get('CSRF_TOKEN'):
        return False
    return secrets.compare_digest(token, current_app.config.get('CSRF_TOKEN', ''))

def csrf_protect(f: Callable) -> Callable:
    """
    Decorator to protect against CSRF attacks
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        # Skip CSRF check for GET requests
        if request.method == 'GET':
            return f(*args, **kwargs)
            
        # Check CSRF token for other methods
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        if not validate_csrf_token(token):
            return Response('CSRF token validation failed', 403)
            
        return f(*args, **kwargs)
    return decorated_function

def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        input_str: Input string to sanitize
        
    Returns:
        Sanitized string
    """
    # Remove potentially dangerous characters
    sanitized = input_str.replace('<', '&lt;').replace('>', '&gt;')
    return sanitized

def setup_security(app: Any) -> None:
    """
    Set up security for a Flask application
    
    Args:
        app: Flask application
    """
    # Generate CSRF token
    app.config['CSRF_TOKEN'] = generate_csrf_token()
    
    # Set secure headers
    @app.after_request
    def set_secure_headers(response: Any) -> Any:
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
        
    # Make CSRF token available to templates
    @app.context_processor
    def inject_csrf_token() -> Dict[str, str]:
        return {'csrf_token': app.config.get('CSRF_TOKEN', '')}
        
    return None
