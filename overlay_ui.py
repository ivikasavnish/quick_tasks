"""
Task input overlay UI.
Displays a centered, translucent input field over a dimmed background.
"""

import ctypes
from ctypes import wintypes
from typing import Callable, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QGraphicsDropShadowEffect,
    QApplication, QLabel
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QPainter, QBrush, QFont, QKeyEvent


# Windows DWM constants for blur effect
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWM_SYSTEMBACKDROP_TYPE = 38
DWMSBT_MAINWINDOW = 2
DWMSBT_TRANSIENTWINDOW = 3
DWMSBT_TABBEDWINDOW = 4


def enable_blur_behind(hwnd: int):
    """Enable Windows acrylic/blur effect behind window."""
    try:
        dwmapi = ctypes.windll.dwmapi
        
        # Try Windows 11 Mica/Acrylic first
        value = ctypes.c_int(DWMSBT_TRANSIENTWINDOW)
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWM_SYSTEMBACKDROP_TYPE,
            ctypes.byref(value),
            ctypes.sizeof(value)
        )
        
        # Enable dark mode for better contrast
        dark = ctypes.c_int(1)
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(dark),
            ctypes.sizeof(dark)
        )
    except Exception:
        pass  # Fallback to semi-transparent background


class DimBackground(QWidget):
    """Full-screen dimmed background overlay."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._opacity = 0.0
        self._target_opacity = 0.6
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, int(255 * self._opacity)))
        
    def fade_in(self, duration: int = 150):
        """Animate fade in."""
        self._animate_opacity(self._target_opacity, duration)
        
    def fade_out(self, duration: int = 100):
        """Animate fade out."""
        self._animate_opacity(0.0, duration)
        
    def _animate_opacity(self, target: float, duration: int):
        """Animate opacity change."""
        steps = max(1, duration // 16)  # ~60fps
        step_size = (target - self._opacity) / steps
        
        def step():
            self._opacity += step_size
            if (step_size > 0 and self._opacity >= target) or \
               (step_size < 0 and self._opacity <= target):
                self._opacity = target
                self.update()
                return
            self.update()
            QTimer.singleShot(16, step)
            
        step()


class TaskInput(QLineEdit):
    """Styled task input field."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Add a task...")
        self._setup_style()
        
    def _setup_style(self):
        """Apply minimal, clean styling."""
        self.setFont(QFont("Segoe UI", 16))
        self.setMinimumHeight(50)
        
        self.setStyleSheet("""
            QLineEdit {
                background-color: rgba(30, 30, 30, 220);
                color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                selection-background-color: #0078d4;
            }
            QLineEdit:focus {
                background-color: rgba(40, 40, 40, 240);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        
        # Add subtle shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


class TaskOverlay(QWidget):
    """
    Main overlay widget with dimmed background and centered input.
    """
    
    def __init__(self, on_submit: Callable[[str], None], parent=None):
        super().__init__(parent)
        self.on_submit = on_submit
        self.on_cancel: Optional[Callable[[], None]] = None
        
        self._setup_window()
        self._setup_ui()
        self._dim_background = DimBackground()
        
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def _setup_ui(self):
        """Set up the overlay layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Container for input with proper sizing
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Task input field
        self.input_field = TaskInput()
        self.input_field.returnPressed.connect(self._on_submit)
        container_layout.addWidget(self.input_field)
        
        # Hint label
        self.hint_label = QLabel("Press Enter to add • Esc to cancel")
        self.hint_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.4);
                font-size: 11px;
                padding-top: 8px;
            }
        """)
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.hint_label)
        
        layout.addWidget(self.container)
        
    def show_overlay(self):
        """Display the overlay centered on screen."""
        screen = QApplication.primaryScreen()
        if not screen:
            return
            
        screen_geo = screen.geometry()
        
        # Size: 30% of screen width
        width = int(screen_geo.width() * 0.3)
        height = 120
        
        # Center position
        x = screen_geo.x() + (screen_geo.width() - width) // 2
        y = screen_geo.y() + (screen_geo.height() - height) // 2
        
        # Show dim background
        self._dim_background.setGeometry(screen_geo)
        self._dim_background.show()
        self._dim_background.fade_in()
        
        # Position and show overlay
        self.setGeometry(x, y, width, height)
        self.show()
        
        # Enable blur effect (Windows 11)
        try:
            hwnd = int(self.winId())
            enable_blur_behind(hwnd)
        except Exception:
            pass
            
        # Focus input
        self.input_field.clear()
        self.input_field.setFocus()
        self.activateWindow()
        
    def hide_overlay(self):
        """Hide the overlay with animation."""
        self._dim_background.fade_out()
        QTimer.singleShot(100, self._dim_background.hide)
        self.hide()
        
    def _on_submit(self):
        """Handle task submission."""
        text = self.input_field.text().strip()
        if text:
            self.on_submit(text)
        self.hide_overlay()
        
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key events."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide_overlay()
            if self.on_cancel:
                self.on_cancel()
        else:
            super().keyPressEvent(event)
            
    def focusOutEvent(self, event):
        """Hide overlay when focus is lost."""
        # Small delay to allow for intentional clicks elsewhere
        QTimer.singleShot(100, self._check_focus)
        super().focusOutEvent(event)
        
    def _check_focus(self):
        """Check if we should hide due to lost focus."""
        if self.isVisible() and not self.isActiveWindow():
            # Don't hide if input still has focus
            if not self.input_field.hasFocus():
                self.hide_overlay()


class LightTaskOverlay(TaskOverlay):
    """Light mode variant of the overlay."""
    
    def _setup_ui(self):
        super()._setup_ui()
        
        # Override with light theme
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 240);
                color: #1a1a1a;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 12px;
                padding: 12px 20px;
                selection-background-color: #0078d4;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            QLineEdit::placeholder {
                color: rgba(0, 0, 0, 0.4);
            }
        """)
        
        self.hint_label.setStyleSheet("""
            QLabel {
                color: rgba(0, 0, 0, 0.5);
                font-size: 11px;
                padding-top: 8px;
            }
        """)
