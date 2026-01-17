"""
Cross-platform startup manager.
Manages auto-start on system boot for Windows, Mac, and Linux.
"""

import logging
import platform
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class StartupManager:
    """
    Cross-platform startup manager.
    Handles auto-start configuration for Windows, Mac, and Linux.
    """
    
    def __init__(self):
        """Initialize startup manager."""
        self._platform = platform.system()
        self.app_name = "QuickTasks"
        
    def enable(self) -> bool:
        """
        Enable auto-start on system boot.
        
        Returns:
            True if successful
        """
        try:
            if self._platform == "Windows":
                return self._enable_windows()
            elif self._platform == "Darwin":  # macOS
                return self._enable_macos()
            elif self._platform == "Linux":
                return self._enable_linux()
            else:
                logger.warning(f"Auto-start not supported on {self._platform}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to enable auto-start: {e}")
            return False
    
    def disable(self) -> bool:
        """
        Disable auto-start on system boot.
        
        Returns:
            True if successful
        """
        try:
            if self._platform == "Windows":
                return self._disable_windows()
            elif self._platform == "Darwin":
                return self._disable_macos()
            elif self._platform == "Linux":
                return self._disable_linux()
            else:
                logger.warning(f"Auto-start not supported on {self._platform}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to disable auto-start: {e}")
            return False
    
    def is_enabled(self) -> bool:
        """
        Check if auto-start is enabled.
        
        Returns:
            True if enabled
        """
        try:
            if self._platform == "Windows":
                return self._is_enabled_windows()
            elif self._platform == "Darwin":
                return self._is_enabled_macos()
            elif self._platform == "Linux":
                return self._is_enabled_linux()
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to check auto-start status: {e}")
            return False
    
    # Windows implementation
    def _enable_windows(self) -> bool:
        """Enable auto-start on Windows."""
        import winreg
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        exe_path = sys.executable
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, 
                               winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            logger.info("Enabled auto-start on Windows")
            return True
        except Exception as e:
            logger.error(f"Windows registry error: {e}")
            return False
    
    def _disable_windows(self) -> bool:
        """Disable auto-start on Windows."""
        import winreg
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                               winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, self.app_name)
            winreg.CloseKey(key)
            logger.info("Disabled auto-start on Windows")
            return True
        except FileNotFoundError:
            # Key doesn't exist, already disabled
            return True
        except Exception as e:
            logger.error(f"Windows registry error: {e}")
            return False
    
    def _is_enabled_windows(self) -> bool:
        """Check if auto-start is enabled on Windows."""
        import winreg
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                               winreg.KEY_READ)
            winreg.QueryValueEx(key, self.app_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    # macOS implementation
    def _enable_macos(self) -> bool:
        """Enable auto-start on macOS using LaunchAgents."""
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        launch_agents_dir.mkdir(parents=True, exist_ok=True)
        
        plist_path = launch_agents_dir / f"com.{self.app_name.lower()}.plist"
        exe_path = sys.executable
        
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.{self.app_name.lower()}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
"""
        
        try:
            plist_path.write_text(plist_content)
            logger.info(f"Enabled auto-start on macOS: {plist_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create LaunchAgent: {e}")
            return False
    
    def _disable_macos(self) -> bool:
        """Disable auto-start on macOS."""
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        plist_path = launch_agents_dir / f"com.{self.app_name.lower()}.plist"
        
        try:
            if plist_path.exists():
                plist_path.unlink()
            logger.info("Disabled auto-start on macOS")
            return True
        except Exception as e:
            logger.error(f"Failed to remove LaunchAgent: {e}")
            return False
    
    def _is_enabled_macos(self) -> bool:
        """Check if auto-start is enabled on macOS."""
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        plist_path = launch_agents_dir / f"com.{self.app_name.lower()}.plist"
        return plist_path.exists()
    
    # Linux implementation
    def _enable_linux(self) -> bool:
        """Enable auto-start on Linux using XDG autostart."""
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = autostart_dir / f"{self.app_name.lower()}.desktop"
        exe_path = sys.executable
        
        desktop_content = f"""[Desktop Entry]
Type=Application
Name={self.app_name}
Exec={exe_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
        
        try:
            desktop_file.write_text(desktop_content)
            logger.info(f"Enabled auto-start on Linux: {desktop_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create autostart file: {e}")
            return False
    
    def _disable_linux(self) -> bool:
        """Disable auto-start on Linux."""
        autostart_dir = Path.home() / ".config" / "autostart"
        desktop_file = autostart_dir / f"{self.app_name.lower()}.desktop"
        
        try:
            if desktop_file.exists():
                desktop_file.unlink()
            logger.info("Disabled auto-start on Linux")
            return True
        except Exception as e:
            logger.error(f"Failed to remove autostart file: {e}")
            return False
    
    def _is_enabled_linux(self) -> bool:
        """Check if auto-start is enabled on Linux."""
        autostart_dir = Path.home() / ".config" / "autostart"
        desktop_file = autostart_dir / f"{self.app_name.lower()}.desktop"
        return desktop_file.exists()
