#!/usr/bin/env python3
"""
Main web application for the Cubey robot.

This module provides a Flask-based web interface for controlling the Cubey robot.
It includes routes for the main page, video streaming, and API endpoints.
"""

import os
import sys
import signal
from typing import Generator, Optional

from flask import Flask, render_template, Response

from cubey.web.camera import Camera
from cubey.web.integration import CubeyWebIntegration, create_api_routes
from cubey.config.loader import get_merged_config

app = Flask(__name__)
cam: Optional[Camera] = None
integration: Optional[CubeyWebIntegration] = None

def signal_handler(sig: int, frame: Optional[object]) -> None:
    """
    Handle Ctrl+C to gracefully shut down the application.
    
    Args:
        sig: Signal number
        frame: Current stack frame
    """
    print('Shutting down...')
    if cam is not None:
        cam.stop()
    sys.exit(0)

def gen(camera: Camera) -> Generator[bytes, None, None]:
    """
    Video streaming generator function.
    
    Args:
        camera: Camera instance
        
    Yields:
        JPEG frames for streaming
    """
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame if frame is not None else b'' + b'\r\n')

@app.route('/')
def index() -> str:
    """
    Main page route.
    
    Returns:
        Rendered HTML template
    """
    return render_template('index.html')

@app.route('/video_feed')
def video_feed() -> Response:
    """
    Video streaming route.
    
    Returns:
        Streaming response
    """
    global cam
    cam = Camera(0)
    return Response(gen(cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def main(host: str = '0.0.0.0', port: int = 5000, config_path: Optional[str] = None) -> None:
    """
    Main entry point for the web application.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        config_path: Path to configuration file
    """
    global integration
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Load configuration
    config = get_merged_config(config_path)
    
    # Initialize the integration
    try:
        integration = CubeyWebIntegration(config)
        
        # Create API routes
        create_api_routes(app, integration)
        
        # Get web configuration
        web_config = config.get("web", {})
        host = web_config.get("host", host)
        port = web_config.get("port", port)
        debug = web_config.get("debug", False)
        
        # Start the Flask app
        print(f"Starting web server on http://{host}:{port}")
        app.run(host=host, port=port, threaded=True, debug=debug)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
