#!/usr/bin/env python3
"""
Quick Tasks - Instantly add tasks to Google Tasks via global hotkey.
A lightweight Windows background utility for power users.
"""

import sys
import os
import logging
from pathlib import Path

# Configure logging (minimal, no task text logged)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Ensure we're running from the correct directory for relative imports
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent

# Add app directory to path
sys.path.insert(0, str(APP_DIR))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from quick_tasks.tray_manager import TrayManager
from quick_tasks.overlay_ui import TaskOverlay
from quick_tasks.config import Config
from quick_tasks.storage.factory import StorageFactory

# Use cross-platform managers
try:
    from quick_tasks.hotkey_manager_xplatform import HotkeyManager
except ImportError:
    from quick_tasks.hotkey_manager import HotkeyManager

try:
    from quick_tasks.startup_manager_xplatform import StartupManager
except ImportError:
    from quick_tasks.startup_manager import StartupManager


class QuickTasksApp:
    """Main application controller."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("Quick Tasks")
        
        # Set application icon
        icon_path = APP_DIR / "resources" / "icon.ico"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))
        
        # Initialize configuration
        self.config = Config(APP_DIR / "config")
        
        # Initialize storage backend
        backend_type = self.config.get("storage_backend", "local")
        self.storage_backend = StorageFactory.create(backend_type, self.config)
        
        if not self.storage_backend:
            logger.error(f"Failed to initialize storage backend: {backend_type}")
            # Fall back to local storage
            self.storage_backend = StorageFactory.create("local", self.config)
        
        # Initialize components
        self.overlay = TaskOverlay(self._on_task_submit)
        self.hotkey_manager = HotkeyManager(self._on_hotkey_pressed)
        self.tray_manager = TrayManager(
            on_quit=self._on_quit,
            on_auth=self._on_reauth,
            on_toggle_startup=self._on_toggle_startup,
            config=self.config
        )
        self.startup_manager = StartupManager()
        
        # Connect overlay escape handler
        self.overlay.on_cancel = self._on_overlay_cancel
        
    def _on_hotkey_pressed(self):
        """Handle global hotkey press."""
        logger.info("Hotkey pressed!")
        if not self.overlay.isVisible():
            logger.info("Showing overlay...")
            self.overlay.show_overlay()
    
    def _on_task_submit(self, task_text: str):
        """Handle task submission from overlay."""
        if not task_text.strip():
            return
        
        # Submit task in background (non-blocking)
        QTimer.singleShot(0, lambda: self._submit_task_async(task_text))
    
    def _submit_task_async(self, task_text: str):
        """Submit task to storage backend."""
        try:
            success = self.storage_backend.add_task(task_text)
            if success:
                backend_name = self.storage_backend.backend_name
                self.tray_manager.show_notification("Task Added", f"Task saved to {backend_name}")
            else:
                self.tray_manager.show_notification("Error", "Failed to add task", error=True)
        except Exception as e:
            logger.error(f"Task submission failed: {type(e).__name__}")
            self.tray_manager.show_notification("Error", "Failed to add task", error=True)
    
    def _on_overlay_cancel(self):
        """Handle overlay cancellation."""
        pass  # Overlay handles its own hiding
    
    def _on_quit(self):
        """Handle application quit."""
        self.hotkey_manager.stop()
        self.app.quit()
    
    def _on_reauth(self):
        """Handle re-authentication request."""
        try:
            # Only authenticate if using a backend that requires it
            if hasattr(self.storage_backend, 'authenticate'):
                self.storage_backend.clear_credentials()
                if self.storage_backend.authenticate():
                    backend_name = self.storage_backend.backend_name
                    self.tray_manager.show_notification("Success", f"Re-authenticated with {backend_name}")
                else:
                    self.tray_manager.show_notification("Error", "Authentication failed", error=True)
            else:
                self.tray_manager.show_notification("Info", "This storage backend doesn't require authentication")
        except Exception as e:
            logger.error(f"Re-auth failed: {type(e).__name__}")
            self.tray_manager.show_notification("Error", "Authentication failed", error=True)
    
    def _on_toggle_startup(self, enabled: bool):
        """Toggle startup with Windows."""
        if enabled:
            self.startup_manager.enable()
        else:
            self.startup_manager.disable()
        self.config.set("start_with_windows", enabled)
    
    def run(self):
        """Start the application."""
        # Check if backend is ready
        if not self.storage_backend.is_ready():
            backend_name = self.storage_backend.backend_name
            self.tray_manager.show_notification(
                "Setup Required", 
                f"Right-click tray icon → Configure {backend_name}"
            )
        
        # Start hotkey listener
        self.hotkey_manager.start()
        
        # Show tray icon
        self.tray_manager.show()
        
        # Run event loop
        return self.app.exec()


def main():
    """Application entry point."""
    # Prevent multiple instances
    from PySide6.QtNetwork import QLocalServer, QLocalSocket
    
    socket = QLocalSocket()
    socket.connectToServer("QuickTasksInstance")
    if socket.waitForConnected(500):
        # Another instance is running
        logger.warning("Another instance is already running")
        sys.exit(0)
    
    # Create server for single instance check
    server = QLocalServer()
    server.removeServer("QuickTasksInstance")
    server.listen("QuickTasksInstance")
    
    try:
        app = QuickTasksApp()
        sys.exit(app.run())
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
