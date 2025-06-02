#!/usr/bin/env python3
import os
import sys
import signal
from flask import Flask, render_template, Response
from cubey.web.camera import Camera
from cubey.web.integration import CubeyWebIntegration, create_api_routes

"""
Main web application for the cubey project
"""

app = Flask(__name__)
cam = None
integration = None

def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully shut down the application"""
    print('Shutting down...')
    if cam is not None:
        cam.stop()
    sys.exit(0)

def gen(camera):
    """Video streaming generator function"""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame if frame is not None else b'' + b'\r\n')

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    global cam
    cam = Camera(0)
    return Response(gen(cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def main():
    """Main entry point for the web application"""
    global integration
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Get the absolute path to the config file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    config_path = os.path.join(parent_dir, 'config.yaml')
    
    # Initialize the integration
    try:
        integration = CubeyWebIntegration(config_path)
        
        # Create API routes
        create_api_routes(app, integration)
        
        # Start the Flask app
        print("Starting web server on http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
