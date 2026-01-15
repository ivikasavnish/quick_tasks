"""
Windows startup manager.
Handles auto-start registration via Windows Registry.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Registry key for startup programs
STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "QuickTasks"


class StartupManager:
    """
    Manages application auto-start with Windows.
    Uses the Windows Registry Run key.
    """
    
    def __init__(self, app_name: str = APP_NAME):
        """
        Initialize startup manager.
        
        Args:
            app_name: Name to use in registry
        """
        self.app_name = app_name
        self._executable = self._get_executable_path()
        
    def _get_executable_path(self) -> str:
        """Get the path to the current executable."""
        if getattr(sys, 'frozen', False):
            # Running as compiled .exe
            return sys.executable
        else:
            # Running as script - use pythonw to avoid console
            python = sys.executable
            script = Path(__file__).parent / "main.py"
            return f'"{python}" "{script}"'
            
    def is_enabled(self) -> bool:
        """Check if auto-start is enabled."""
        try:
            import winreg
            
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                STARTUP_KEY,
                0,
                winreg.KEY_READ
            ) as key:
                try:
                    winreg.QueryValueEx(key, self.app_name)
                    return True
                except WindowsError:
                    return False
                    
        except Exception as e:
            logger.warning(f"Failed to check startup status: {e}")
            return False
            
    def enable(self) -> bool:
        """
        Enable auto-start with Windows.
        
        Returns:
            True if successful
        """
        try:
            import winreg
            
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                STARTUP_KEY,
                0,
                winreg.KEY_WRITE
            ) as key:
                winreg.SetValueEx(
                    key,
                    self.app_name,
                    0,
                    winreg.REG_SZ,
                    self._executable
                )
                
            logger.info("Enabled auto-start")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable startup: {e}")
            return False
            
    def disable(self) -> bool:
        """
        Disable auto-start with Windows.
        
        Returns:
            True if successful
        """
        try:
            import winreg
            
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                STARTUP_KEY,
                0,
                winreg.KEY_WRITE
            ) as key:
                try:
                    winreg.DeleteValue(key, self.app_name)
                except WindowsError:
                    pass  # Already not present
                    
            logger.info("Disabled auto-start")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable startup: {e}")
            return False
            
    def toggle(self) -> bool:
        """
        Toggle auto-start state.
        
        Returns:
            New state (True = enabled)
        """
        if self.is_enabled():
            self.disable()
            return False
        else:
            self.enable()
            return True


class TaskSchedulerStartup:
    """
    Alternative startup manager using Windows Task Scheduler.
    Provides more control (e.g., delayed start, elevated privileges).
    """
    
    def __init__(self, app_name: str = APP_NAME):
        self.app_name = app_name
        self._executable = self._get_executable_path()
        
    def _get_executable_path(self) -> str:
        if getattr(sys, 'frozen', False):
            return sys.executable
        else:
            return f'{sys.executable}" "{Path(__file__).parent / "main.py"}'
            
    def enable(self, delay_seconds: int = 10) -> bool:
        """
        Enable startup via Task Scheduler with optional delay.
        
        Args:
            delay_seconds: Seconds to wait after login before starting
            
        Returns:
            True if successful
        """
        try:
            import subprocess
            
            # Create scheduled task via schtasks command
            cmd = [
                'schtasks', '/create',
                '/tn', f'\\{self.app_name}',
                '/tr', f'"{self._executable}"',
                '/sc', 'onlogon',
                '/delay', f'0000:{delay_seconds:02d}',
                '/f',  # Force overwrite
                '/rl', 'limited'  # Run with limited privileges
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to create scheduled task: {e}")
            return False
            
    def disable(self) -> bool:
        """Disable startup by removing scheduled task."""
        try:
            import subprocess
            
            cmd = ['schtasks', '/delete', '/tn', f'\\{self.app_name}', '/f']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to delete scheduled task: {e}")
            return False
            
    def is_enabled(self) -> bool:
        """Check if scheduled task exists."""
        try:
            import subprocess
            
            cmd = ['schtasks', '/query', '/tn', f'\\{self.app_name}']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            return result.returncode == 0
            
        except Exception:
            return False
