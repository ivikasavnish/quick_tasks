# Quick Start Guide

Welcome to Quick Tasks! This guide will help you get started in minutes.

## Installation

### 1. Install Python
Make sure you have Python 3.8 or newer installed:
```bash
python --version  # or python3 --version
```

### 2. Install Quick Tasks
```bash
pip install quick-tasks
```

Or from source:
```bash
git clone https://github.com/ivikasavnish/quick_tasks.git
cd quick_tasks
pip install -e .
```

## First Run

### Start the Application
```bash
quick-tasks
```

On first run:
- A system tray icon will appear
- Configuration directory will be created
- Local storage is enabled by default (no setup needed!)

### Using Quick Tasks

1. **Press** `Ctrl+Shift+P` (from anywhere on your system)
2. **Type** your task
3. **Press** `Enter`
4. **Done!** Your task is saved

### View Your Tasks

Tasks are stored in:
- **Linux/Mac**: `~/.config/quick_tasks/tasks.json`
- **Windows**: `%APPDATA%/quick_tasks/tasks.json`

You can open this file in any text editor to view your tasks.

## Configuration

### Change Storage Backend

Edit the settings file:
- **Linux/Mac**: `~/.config/quick_tasks/settings.json`
- **Windows**: `%APPDATA%/quick_tasks/settings.json`

Available backends:
- `"local"` - Local JSON file storage (default, no setup needed)
- `"google"` - Google Tasks (requires setup, see below)

Example settings.json:
```json
{
  "start_with_windows": false,
  "hotkey": "ctrl+shift+p",
  "theme": "dark",
  "show_notifications": true,
  "overlay_width_percent": 30,
  "storage_backend": "local"
}
```

## Google Tasks Setup (Optional)

If you want to sync tasks with Google Tasks:

### 1. Update Storage Backend
Edit `settings.json` and change:
```json
{
  "storage_backend": "google"
}
```

### 2. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Tasks API
4. Configure OAuth consent screen
5. Create OAuth credentials (Desktop app)
6. Download credentials as `credentials.json`

### 3. Place Credentials File

Put `credentials.json` in your config directory:
- **Linux/Mac**: `~/.config/quick_tasks/credentials.json`
- **Windows**: `%APPDATA%/quick_tasks/credentials.json`

### 4. Authenticate

1. Right-click the system tray icon
2. Select "Re-authenticate"
3. Follow browser prompts
4. Grant permissions
5. Done!

For detailed Google setup, see the main [README.md](README.md#google-tasks-setup-detailed).

## Platform-Specific Notes

### macOS
- You may need to grant accessibility permissions
- Go to: System Preferences → Security & Privacy → Privacy → Accessibility
- Add your terminal application

### Linux
- Works with X11 and Wayland
- No special setup needed
- If hotkey doesn't work, you may need to install: `sudo apt install python3-xlib`

### Windows
- Works on Windows 10/11
- No special setup needed

## Troubleshooting

### Hotkey Not Working
1. Make sure no other application is using `Ctrl+Shift+P`
2. On macOS, grant accessibility permissions
3. On Linux, ensure X11 or Wayland is running

### Can't Start Application
1. Make sure all dependencies are installed: `pip install quick-tasks`
2. Check Python version: `python --version` (needs 3.8+)
3. Try running with verbose logging: `quick-tasks --verbose` (if implemented)

### System Tray Icon Not Appearing
1. Make sure your desktop environment supports system tray
2. On some Linux environments, you may need to enable system tray extensions
3. Check if the application is running: `ps aux | grep quick-tasks`

## Advanced Usage

### Auto-Start on Boot
1. Right-click system tray icon
2. Select "Start with System"
3. The application will now start automatically on login

### Changing the Hotkey
Currently, the hotkey is fixed to `Ctrl+Shift+P`. Custom hotkey support may be added in future versions.

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/ivikasavnish/quick_tasks/issues)
- **Documentation**: [README.md](README.md)
- **Source Code**: [GitHub Repository](https://github.com/ivikasavnish/quick_tasks)

## Next Steps

- Explore the [full documentation](README.md)
- Configure Google Tasks backend (optional)
- Enable auto-start
- Customize settings
- Build from source

Happy task capturing! 🚀
