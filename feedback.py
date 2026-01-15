"""
Optional feedback effects.
Provides subtle sound and visual feedback on task creation.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class FeedbackManager:
    """
    Manages user feedback for task operations.
    Provides sound and visual cues.
    """
    
    def __init__(self, config):
        """
        Initialize feedback manager.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self._sound_enabled = config.get("sound_feedback", True)
        
    def task_added(self):
        """Play feedback when task is added successfully."""
        if self._sound_enabled:
            self._play_success_sound()
            
    def task_failed(self):
        """Play feedback when task fails."""
        if self._sound_enabled:
            self._play_error_sound()
            
    def _play_success_sound(self):
        """Play success sound using Windows API."""
        try:
            import winsound
            # Play a subtle system sound
            winsound.MessageBeep(winsound.MB_OK)
        except Exception:
            pass  # Sound is optional, don't fail
            
    def _play_error_sound(self):
        """Play error sound."""
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONHAND)
        except Exception:
            pass
            

class AnimationManager:
    """
    Manages subtle animations for the overlay.
    """
    
    @staticmethod
    def flash_success(widget):
        """
        Flash the widget border green briefly to indicate success.
        
        Args:
            widget: QWidget to animate
        """
        try:
            from PySide6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
            from PySide6.QtGui import QColor
            
            original_style = widget.styleSheet()
            
            # Flash green
            widget.setStyleSheet(
                original_style + 
                "border: 2px solid #10b981;"
            )
            
            # Restore after delay
            QTimer.singleShot(200, lambda: widget.setStyleSheet(original_style))
            
        except Exception:
            pass  # Animation is optional


class OverlayAnimations:
    """
    Fade and slide animations for the overlay.
    """
    
    @staticmethod
    def fade_in(widget, duration: int = 150):
        """
        Fade in animation.
        
        Args:
            widget: Widget to animate
            duration: Animation duration in ms
        """
        try:
            from PySide6.QtCore import QPropertyAnimation, QEasingCurve
            from PySide6.QtWidgets import QGraphicsOpacityEffect
            
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(duration)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.start()
            
            # Store reference to prevent garbage collection
            widget._fade_anim = anim
            
        except Exception:
            pass
            
    @staticmethod
    def fade_out(widget, duration: int = 100, on_finished=None):
        """
        Fade out animation.
        
        Args:
            widget: Widget to animate
            duration: Animation duration in ms
            on_finished: Callback when animation completes
        """
        try:
            from PySide6.QtCore import QPropertyAnimation, QEasingCurve
            from PySide6.QtWidgets import QGraphicsOpacityEffect
            
            effect = widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)
                effect.setOpacity(1)
            
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(duration)
            anim.setStartValue(1)
            anim.setEndValue(0)
            anim.setEasingCurve(QEasingCurve.Type.InCubic)
            
            if on_finished:
                anim.finished.connect(on_finished)
                
            anim.start()
            widget._fade_anim = anim
            
        except Exception:
            if on_finished:
                on_finished()


class ProgressIndicator:
    """
    Simple progress indicator for async operations.
    """
    
    def __init__(self, parent_widget):
        """
        Initialize progress indicator.
        
        Args:
            parent_widget: Widget to show progress on
        """
        self.parent = parent_widget
        self._spinner = None
        
    def show(self):
        """Show progress indicator."""
        try:
            from PySide6.QtWidgets import QLabel
            from PySide6.QtCore import Qt
            
            if not self._spinner:
                self._spinner = QLabel("...", self.parent)
                self._spinner.setStyleSheet("""
                    QLabel {
                        color: rgba(255, 255, 255, 0.5);
                        font-size: 14px;
                    }
                """)
                self._spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
            self._spinner.show()
            
        except Exception:
            pass
            
    def hide(self):
        """Hide progress indicator."""
        if self._spinner:
            self._spinner.hide()
