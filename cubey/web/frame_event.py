"""
Frame event module for the web interface.

This module provides an event-like class for signaling when new frames are available
from the camera.
"""

import time
import threading
from typing import Dict, Any, List, Callable, Optional

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    from _thread import get_ident


class FrameEvent:
    """
    An Event-like class that signals all active clients when a new frame is available.
    """

    def __init__(self) -> None:
        """
        Initialize the frame event.
        """
        self.events: Dict[Any, Dict[str, Any]] = {}
        self.latest_frame: Optional[bytes] = None
        self.listeners: List[Callable[[bytes], None]] = []
        self.lock = threading.Lock()

    def wait(self) -> bool:
        """
        Invoked from each client's thread to wait for the next frame.
        
        Returns:
            True when the event is set
        """
        ident = get_ident()
        if ident not in self.events:
            # This is a new client
            # Add an entry for it in the self.events dict
            # Each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self) -> None:
        """
        Invoked by the camera thread when a new frame is available.
        """
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # If this client's event is not set, then set it
                # Also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # If the client's event is already set, it means the client
                # did not process a previous frame
                # If the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self) -> None:
        """
        Invoked from each client's thread after a frame was processed.
        """
        ident = get_ident()
        if ident in self.events:
            self.events[ident][0].clear()
            
    def on_new_frame(self, frame: bytes) -> None:
        """
        Called when a new frame is available.
        
        Args:
            frame: JPEG encoded frame
        """
        with self.lock:
            self.latest_frame = frame
            
        # Notify all listeners
        for listener in self.listeners:
            try:
                listener(frame)
            except Exception as e:
                print(f"Error in frame listener: {e}")
                
        # Set the event for all waiting clients
        self.set()
        
    def get_latest_frame(self) -> Optional[bytes]:
        """
        Get the latest frame.
        
        Returns:
            JPEG encoded frame or None if no frame is available
        """
        with self.lock:
            return self.latest_frame
            
    def add_listener(self, callback: Callable[[bytes], None]) -> None:
        """
        Add a listener for new frames.
        
        Args:
            callback: Function to call when a new frame is available
        """
        if callback not in self.listeners:
            self.listeners.append(callback)
            
    def remove_listener(self, callback: Callable[[bytes], None]) -> None:
        """
        Remove a frame listener.
        
        Args:
            callback: Function to remove
        """
        if callback in self.listeners:
            self.listeners.remove(callback)
