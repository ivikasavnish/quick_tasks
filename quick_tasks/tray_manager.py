"""
System tray manager.
Provides tray icon with menu for app control.
"""

import logging
from typing import Callable, Optional

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QBrush
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)


def create_default_icon() -> QIcon:
    """Create a simple default icon if no icon file exists."""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw a checkmark circle
    painter.setBrush(QBrush(QColor("#0078d4")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, size - 8, size - 8)
    
    # Draw checkmark
    painter.setPen(QColor("#ffffff"))
    from PySide6.QtGui import QPen
    pen = QPen(QColor("#ffffff"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    
    # Checkmark path
    painter.drawLine(18, 32, 28, 42)
    painter.drawLine(28, 42, 46, 22)
    
    painter.end()
    
    return QIcon(pixmap)


class TrayManager:
    """
    Manages system tray icon and context menu.
    """
    
    def __init__(
        self,
        on_quit: Callable[[], None],
        on_auth: Callable[[], None],
        on_toggle_startup: Callable[[bool], None],
        config,
        icon_path: Optional[str] = None
    ):
        """
        Initialize tray manager.
        
        Args:
            on_quit: Callback for quit action
            on_auth: Callback for re-authentication
            on_toggle_startup: Callback for toggling startup
            config: Config instance
            icon_path: Optional path to custom icon
        """
        self.on_quit = on_quit
        self.on_auth = on_auth
        self.on_toggle_startup = on_toggle_startup
        self.config = config
        
        # Create tray icon
        self.tray = QSystemTrayIcon()
        
        # Set icon
        if icon_path:
            self.tray.setIcon(QIcon(icon_path))
        else:
            self.tray.setIcon(create_default_icon())
            
        self.tray.setToolTip("Quick Tasks - Ctrl+Shift+P to add task")
        
        # Create context menu
        self._create_menu()
        
        # Connect signals
        self.tray.activated.connect(self._on_activated)
        
    def _create_menu(self):
        """Create the context menu."""
        menu = QMenu()
        
        # Title / Status
        title_action = QAction("Quick Tasks", menu)
        title_action.setEnabled(False)
        menu.addAction(title_action)
        
        menu.addSeparator()
        
        # Hotkey hint
        hotkey_action = QAction("Ctrl+Shift+P to add task", menu)
        hotkey_action.setEnabled(False)
        menu.addAction(hotkey_action)
        
        menu.addSeparator()
        
        # Authentication
        auth_action = QAction("Re-authenticate Google", menu)
        auth_action.triggered.connect(self.on_auth)
        menu.addAction(auth_action)
        
        menu.addSeparator()
        
        # Start with Windows
        self.startup_action = QAction("Start with Windows", menu)
        self.startup_action.setCheckable(True)
        self.startup_action.setChecked(self.config.get("start_with_windows", False))
        self.startup_action.triggered.connect(self._on_startup_toggled)
        menu.addAction(self.startup_action)
        
        menu.addSeparator()
        
        # Quit
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self.on_quit)
        menu.addAction(quit_action)
        
        self.tray.setContextMenu(menu)
        self.menu = menu
        
    def _on_startup_toggled(self, checked: bool):
        """Handle startup toggle."""
        self.on_toggle_startup(checked)
        
    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Could show overlay or settings on double-click
            pass
            
    def show(self):
        """Show the tray icon."""
        self.tray.show()
        
    def hide(self):
        """Hide the tray icon."""
        self.tray.hide()
        
    def show_notification(
        self,
        title: str,
        message: str,
        error: bool = False,
        duration_ms: int = 2000
    ):
        """
        Show a system notification.
        
        Args:
            title: Notification title
            message: Notification message
            error: If True, show as warning icon
            duration_ms: Display duration
        """
        icon = (
            QSystemTrayIcon.MessageIcon.Warning if error
            else QSystemTrayIcon.MessageIcon.Information
        )
        self.tray.showMessage(title, message, icon, duration_ms)
        
    def update_startup_state(self, enabled: bool):
        """Update the startup menu item state."""
        self.startup_action.setChecked(enabled)
