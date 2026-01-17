"""
Cross-platform hotkey manager.
Uses pynput for cross-platform keyboard listening.
Falls back to platform-specific implementations where needed.
"""

import logging
import platform
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class HotkeyManager:
    """
    Cross-platform global hotkey manager.
    Uses pynput for Mac/Linux, Win32 API for Windows.
    """
    
    def __init__(self, callback: Callable):
        """
        Initialize hotkey manager.
        
        Args:
            callback: Function to call when hotkey is pressed
        """
        self.callback = callback
        self._listener = None
        self._running = False
        self._platform = platform.system()
        
        # Try to use pynput for cross-platform support
        try:
            from pynput import keyboard
            self._use_pynput = True
            self._keyboard = keyboard
            logger.info("Using pynput for hotkey management")
        except ImportError:
            self._use_pynput = False
            logger.warning("pynput not available, trying platform-specific implementation")
            
            # On Windows, try Win32 API
            if self._platform == "Windows":
                try:
                    import ctypes
                    self._use_win32 = True
                    logger.info("Using Win32 API for hotkey management")
                except ImportError:
                    self._use_win32 = False
                    logger.error("No hotkey implementation available")
    
    def start(self):
        """Start listening for hotkeys."""
        if self._running:
            return
        
        try:
            if self._use_pynput:
                self._start_pynput()
            elif self._platform == "Windows" and hasattr(self, '_use_win32') and self._use_win32:
                self._start_win32()
            else:
                logger.error("No hotkey implementation available for this platform")
                return False
            
            self._running = True
            logger.info("Hotkey listener started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}")
            return False
    
    def stop(self):
        """Stop listening for hotkeys."""
        if not self._running:
            return
        
        try:
            if self._listener:
                self._listener.stop()
                self._listener = None
            
            self._running = False
            logger.info("Hotkey listener stopped")
            
        except Exception as e:
            logger.error(f"Error stopping hotkey listener: {e}")
    
    def _start_pynput(self):
        """Start pynput-based hotkey listener."""
        from pynput import keyboard
        
        # Define the hotkey combination (Ctrl+Shift+P)
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+<shift>+p'),
            self.callback
        )
        
        def for_canonical(f):
            return lambda k: f(self._listener.canonical(k))
        
        # Create listener
        self._listener = keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release)
        )
        
        self._listener.start()
        logger.info("Pynput hotkey listener started (Ctrl+Shift+P)")
    
    def _start_win32(self):
        """Start Win32 API-based hotkey listener (Windows only)."""
        import ctypes
        from ctypes import wintypes
        import threading
        
        # Win32 constants
        MOD_CONTROL = 0x0002
        MOD_SHIFT = 0x0004
        MOD_NOREPEAT = 0x4000
        VK_P = 0x50
        
        user32 = ctypes.windll.user32
        HOTKEY_ID = 1
        
        def hotkey_thread():
            """Thread for Win32 hotkey handling."""
            try:
                # Register hotkey
                if not user32.RegisterHotKey(None, HOTKEY_ID, 
                                            MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_P):
                    logger.error("Failed to register hotkey")
                    return
                
                logger.info("Win32 hotkey registered (Ctrl+Shift+P)")
                
                # Message loop
                msg = wintypes.MSG()
                while self._running:
                    result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                    if result == 0 or result == -1:
                        break
                    
                    if msg.message == 0x0312:  # WM_HOTKEY
                        self.callback()
                    
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
                
            except Exception as e:
                logger.error(f"Win32 hotkey thread error: {e}")
            finally:
                try:
                    user32.UnregisterHotKey(None, HOTKEY_ID)
                except:
                    pass
        
        # Start hotkey thread
        thread = threading.Thread(target=hotkey_thread, daemon=True)
        thread.start()
