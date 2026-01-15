"""
Global hotkey manager using Windows API.
Registers system-wide hotkeys that work regardless of focused application.
"""

import ctypes
import ctypes.wintypes
import threading
import logging
from typing import Callable, Optional

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class HotkeySignalEmitter(QObject):
    """Helper class to emit signals from non-Qt threads."""
    hotkey_pressed = Signal()




# Define missing handle types (not available in ctypes.wintypes)
HICON = ctypes.c_void_p
HCURSOR = ctypes.c_void_p
HBRUSH = ctypes.c_void_p

# Define WNDCLASSW structure (not available in ctypes.wintypes)
class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", ctypes.c_uint),
        ("lpfnWndProc", ctypes.c_void_p),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", ctypes.wintypes.HINSTANCE),
        ("hIcon", HICON),
        ("hCursor", HCURSOR),
        ("hbrBackground", HBRUSH),
        ("lpszMenuName", ctypes.wintypes.LPCWSTR),
        ("lpszClassName", ctypes.wintypes.LPCWSTR),
    ]

# Windows API constants
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

WM_HOTKEY = 0x0312

# Virtual key codes
VK_P = 0x50

# Hotkey ID
HOTKEY_ID = 1


class HotkeyManager:
    """
    Manages global hotkey registration and handling.
    Uses Windows RegisterHotKey API for reliable system-wide capture.
    """

    def __init__(self, callback: Callable[[], None]):
        """
        Initialize hotkey manager.

        Args:
            callback: Function to call when hotkey is pressed
        """
        self.callback = callback
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._hwnd = None
        # Signal emitter for thread-safe callback
        self._emitter = HotkeySignalEmitter()
        self._emitter.hotkey_pressed.connect(callback)
        
    def start(self):
        """Start listening for hotkeys in a background thread."""
        if self._running:
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._run_message_loop, daemon=True)
        self._thread.start()
        
    def stop(self):
        """Stop listening for hotkeys."""
        self._running = False

        # Post quit message to break the message loop
        if self._thread and self._thread.is_alive():
            try:
                # Post WM_QUIT to the thread's message queue
                ctypes.windll.user32.PostThreadMessageW(
                    self._thread.ident, 0x0012, 0, 0  # WM_QUIT
                )
            except Exception:
                pass
            self._thread.join(timeout=1.0)
            
    def _run_message_loop(self):
        """Run the Windows message loop for hotkey events."""
        user32 = ctypes.windll.user32

        # Register hotkey with NULL hwnd (thread message queue)
        modifiers = MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT
        if not user32.RegisterHotKey(None, HOTKEY_ID, modifiers, VK_P):
            error = ctypes.get_last_error()
            logger.error(f"Failed to register hotkey (error: {error})")
            logger.info("Hotkey Ctrl+Shift+P may be in use by another application")
            return

        logger.info("Registered hotkey: Ctrl+Shift+P")

        # Message loop - check messages directly
        msg = ctypes.wintypes.MSG()
        while self._running:
            result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if result == 0 or result == -1:
                break

            # Check for hotkey message
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                logger.info("Hotkey detected in message loop")
                # Emit signal to call callback in main Qt thread
                self._emitter.hotkey_pressed.emit()

        # Cleanup
        user32.UnregisterHotKey(None, HOTKEY_ID)
        logger.info("Hotkey manager stopped")


class FallbackHotkeyManager:
    """
    Fallback hotkey manager using keyboard library.
    Used when Windows API approach fails.
    """
    
    def __init__(self, callback: Callable[[], None]):
        self.callback = callback
        self._hook = None
        
    def start(self):
        """Start listening for hotkeys."""
        try:
            import keyboard
            self._hook = keyboard.add_hotkey('ctrl+shift+p', self._on_hotkey, suppress=False)
            logger.info("Registered hotkey (fallback): Ctrl+Shift+P")
        except Exception as e:
            logger.error(f"Failed to register fallback hotkey: {e}")
            
    def stop(self):
        """Stop listening for hotkeys."""
        try:
            import keyboard
            if self._hook:
                keyboard.remove_hotkey(self._hook)
        except Exception:
            pass
            
    def _on_hotkey(self):
        """Handle hotkey press."""
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self.callback)
