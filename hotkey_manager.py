"""
Global hotkey manager using Windows API.
Registers system-wide hotkeys that work regardless of focused application.
"""

import ctypes
import ctypes.wintypes
import threading
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

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
        if self._hwnd:
            try:
                ctypes.windll.user32.PostMessageW(self._hwnd, 0x0012, 0, 0)  # WM_QUIT
            except Exception:
                pass
                
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
            
    def _run_message_loop(self):
        """Run the Windows message loop for hotkey events."""
        user32 = ctypes.windll.user32
        
        # Create a message-only window for receiving hotkey messages
        WNDPROC = ctypes.WINFUNCTYPE(
            ctypes.c_long,
            ctypes.wintypes.HWND,
            ctypes.c_uint,
            ctypes.wintypes.WPARAM,
            ctypes.wintypes.LPARAM
        )
        
        def wndproc(hwnd, msg, wparam, lparam):
            if msg == WM_HOTKEY:
                if wparam == HOTKEY_ID:
                    # Call callback in main thread via Qt
                    from PySide6.QtCore import QMetaObject, Qt, Q_ARG
                    from PySide6.QtWidgets import QApplication
                    
                    app = QApplication.instance()
                    if app:
                        # Use invokeMethod for thread-safe callback
                        QMetaObject.invokeMethod(
                            app,
                            lambda: self.callback(),
                            Qt.ConnectionType.QueuedConnection
                        )
                return 0
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
        
        # Register window class
        wndclass = ctypes.wintypes.WNDCLASSW()
        wndclass.lpfnWndProc = WNDPROC(wndproc)
        wndclass.hInstance = ctypes.windll.kernel32.GetModuleHandleW(None)
        wndclass.lpszClassName = "QuickTasksHotkey"
        
        atom = user32.RegisterClassW(ctypes.byref(wndclass))
        if not atom:
            logger.error("Failed to register window class")
            return
            
        # Create message-only window (HWND_MESSAGE)
        HWND_MESSAGE = ctypes.wintypes.HWND(-3)
        self._hwnd = user32.CreateWindowExW(
            0,
            wndclass.lpszClassName,
            "QuickTasksHotkeyWindow",
            0,
            0, 0, 0, 0,
            HWND_MESSAGE,
            None,
            wndclass.hInstance,
            None
        )
        
        if not self._hwnd:
            logger.error("Failed to create message window")
            return
            
        # Register hotkey: Ctrl+Shift+P
        modifiers = MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT
        if not user32.RegisterHotKey(self._hwnd, HOTKEY_ID, modifiers, VK_P):
            error = ctypes.get_last_error()
            logger.error(f"Failed to register hotkey (error: {error})")
            logger.info("Hotkey Ctrl+Shift+P may be in use by another application")
            return
            
        logger.info("Registered hotkey: Ctrl+Shift+P")
        
        # Message loop
        msg = ctypes.wintypes.MSG()
        while self._running:
            result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if result == 0 or result == -1:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
            
        # Cleanup
        user32.UnregisterHotKey(self._hwnd, HOTKEY_ID)
        user32.DestroyWindow(self._hwnd)
        user32.UnregisterClassW(wndclass.lpszClassName, wndclass.hInstance)
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
        from PySide6.QtCore import QMetaObject, Qt
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app:
            QMetaObject.invokeMethod(
                app,
                lambda: self.callback(),
                Qt.ConnectionType.QueuedConnection
            )
