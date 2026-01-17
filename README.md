# Quick Tasks

A lightweight utility to instantly add tasks to various task managers using a global keyboard shortcut.

**Press `Ctrl+Shift+P` anywhere → Type your task → Press Enter → Done.**

![Quick Tasks Demo](docs/demo.gif)

## Features

- 🚀 **Instant capture**: Global hotkey works from any application
- 🎨 **Beautiful overlay**: Clean, translucent UI
- 🔒 **Secure**: OAuth 2.0 authentication for cloud backends, tokens stored locally
- 💨 **Fast**: Cold start under 1 second, minimal memory footprint
- 🔄 **Auto-start**: Optional system startup integration
- 📱 **System tray**: Runs silently in background
- 🗄️ **Multiple backends**: Choose between local storage, Google Tasks, and more
- 🌍 **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### From PyPI (Recommended)

```bash
pip install quick-tasks
```

### From Source

```bash
git clone https://github.com/ivikasavnish/quick_tasks.git
cd quick_tasks
pip install -e .
```

## Quick Start

### 1. Install the Package

```bash
pip install quick-tasks
```

### 2. Run Quick Tasks

```bash
quick-tasks
```

On first run, the application will:
1. Create a configuration directory at `~/.config/quick_tasks/` (Linux/Mac) or `%APPDATA%/quick_tasks/` (Windows)
2. Start with local storage by default (no setup required!)
3. Show up in your system tray

## Storage Backends

Quick Tasks supports multiple storage backends:

### Local Storage (Default)

No setup required! Tasks are stored locally in a JSON file.

- **Pros**: No authentication, works offline, completely private
- **Cons**: Tasks only available on this device

### Google Tasks

Store tasks in Google Tasks (sync across devices).

#### Setup Google Tasks Backend

1. Set storage backend in settings:
   - Edit `~/.config/quick_tasks/settings.json`
   - Set `"storage_backend": "google"`

2. **Create Google Cloud Project** (one-time setup):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Tasks API
   - Configure OAuth consent screen
   - Create OAuth credentials (Desktop app)
   - Download `credentials.json`
   - Place it in the config directory

3. **Authenticate**:
   - Right-click the tray icon
   - Select "Re-authenticate"
   - Follow the browser prompts

For detailed Google Cloud setup instructions, see [Google Tasks Setup Guide](#google-tasks-setup-detailed).

## Usage

| Action | Key |
|--------|-----|
| Open task input | `Ctrl+Shift+P` |
| Submit task | `Enter` |
| Cancel | `Esc` |

### System Tray Menu

Right-click the tray icon for options:
- **Re-authenticate**: Authenticate with cloud backend (if using Google Tasks)
- **Start with System**: Enable/disable auto-start
- **Quit**: Close the application

## Configuration

Settings are stored in `settings.json`:

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

### Changing Storage Backend

Edit `settings.json` and change `storage_backend` to:
- `"local"` - Local JSON storage (default)
- `"google"` - Google Tasks

## Platform-Specific Notes

### macOS
- May need to grant accessibility permissions
- Go to System Preferences → Security & Privacy → Privacy → Accessibility
- Add Terminal or your terminal app

### Linux
- Works with X11 and Wayland
- Tested on Ubuntu, Fedora, Arch
- May need to install `python3-tk` for some distributions

### Windows
- Works on Windows 10/11
- Uses native Win32 APIs for optimal performance

## Google Tasks Setup (Detailed)

If you want to use Google Tasks backend, follow these detailed steps:

### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it "Quick Tasks" (or anything you prefer)
4. Click "Create"

### Step 2: Enable Tasks API
1. Go to [APIs & Services → Library](https://console.cloud.google.com/apis/library)
2. Search for "Tasks API"
3. Click "Google Tasks API"
4. Click "Enable"

### Step 3: Configure OAuth Consent Screen
1. Go to [APIs & Services → OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Select "External" (or "Internal" if using Google Workspace)
3. Click "Create"
4. Fill in:
   - App name: "Quick Tasks"
   - User support email: Your email
   - Developer contact: Your email
5. Click "Save and Continue"
6. On "Scopes" page, click "Add or Remove Scopes"
7. Find and select: `https://www.googleapis.com/auth/tasks`
8. Click "Update" then "Save and Continue"
9. On "Test users" page, add your Google email
10. Click "Save and Continue" then "Back to Dashboard"

### Step 4: Create OAuth Credentials
1. Go to [APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Desktop app"
4. Name: "Quick Tasks Desktop"
5. Click "Create"
6. Click "Download JSON"
7. Rename the downloaded file to `credentials.json`
8. Place it in the config directory:
   - Linux/Mac: `~/.config/quick_tasks/credentials.json`
   - Windows: `%APPDATA%/quick_tasks/credentials.json`

## Building Executable

To create a standalone executable:

### Using PyInstaller

```bash
pip install pyinstaller
pyinstaller quick_tasks.spec --clean
```

The executable will be in `dist/QuickTasks` (or `dist/QuickTasks.exe` on Windows).

**Important**: If using Google Tasks, copy your `credentials.json` to the config directory of the built app before distributing.

## Project Structure

```
quick_tasks/
├── quick_tasks/         # Main package
│   ├── __init__.py      # Package initialization
│   ├── main.py          # Application entry point
│   ├── config.py        # Configuration management
│   ├── overlay_ui.py    # Translucent overlay UI (PySide6)
│   ├── tray_manager.py  # System tray icon & menu
│   ├── hotkey_manager_xplatform.py  # Cross-platform hotkey manager
│   ├── startup_manager_xplatform.py # Cross-platform auto-start
│   ├── google_tasks_client.py       # Google Tasks API client
│   ├── storage/         # Storage backends
│   │   ├── __init__.py  # Abstract base class
│   │   ├── local_storage.py  # Local JSON storage
│   │   ├── google_tasks.py   # Google Tasks backend
│   │   └── factory.py   # Backend factory
│   ├── resources/       # Icons and assets
│   └── config/          # Config directory structure
├── pyproject.toml       # Package configuration
├── README.md            # This file
└── LICENSE              # MIT License
```

## Design Decisions

### Storage Backends
- **Pluggable architecture**: Easy to add new backends (Todoist, Microsoft To-Do, etc.)
- **Local-first**: Works offline by default with local storage
- **Optional cloud sync**: Use Google Tasks for multi-device sync

### Why PySide6?
- Cross-platform support (Windows, macOS, Linux)
- Native system tray support (no extra dependencies)
- Better rendering than Tkinter
- MIT license (vs PyQt6's GPL)

### Hotkey Management
- **Cross-platform**: Uses `pynput` for Mac/Linux, Win32 API for Windows
- **Global hotkeys**: Works even when other apps have focus
- **Event-driven**: No polling, minimal CPU usage

### Security Considerations
- Task text is never logged
- OAuth tokens stored locally in `config/token.json`
- Credentials never leave your machine
- No analytics or telemetry

## Troubleshooting

### Hotkey Not Working

1. **Another app using Ctrl+Shift+P**: Some apps (IDEs, browsers) may intercept this shortcut
   - Solution: Check your other apps' shortcut settings

2. **Need admin privileges**: Run as administrator if hotkey doesn't register

3. **Antivirus blocking**: Some antivirus software blocks global keyboard hooks
   - Solution: Add QuickTasks to your antivirus allowlist

### Authentication Issues

1. **"credentials.json not found"**: Make sure you:
   - Downloaded OAuth credentials from Google Cloud Console
   - Renamed the file to `credentials.json`
   - Placed it in the `config/` folder

2. **"Access blocked: This app's request is invalid"**: 
   - Make sure you added your email to "Test users" in OAuth consent screen
   - Wait a few minutes after adding yourself as a test user

3. **Token expired errors**:
   - Right-click tray icon → "Re-authenticate Google"

### Overlay Not Appearing

1. **Multiple monitors**: Overlay appears on primary monitor
2. **DPI scaling**: If overlay looks wrong, check Windows display scaling
3. **Focus issues**: Some fullscreen apps (games) may prevent overlay

## Extending the App

### Adding Natural Language Dates

Install dateparser:
```bash
pip install dateparser
```

Modify `google_tasks_client.py` to use `DateParser.parse()`.

### Custom Task Lists

Use `GoogleTasksClient.get_tasklists()` to list available task lists, then pass `tasklist_id` to `add_task()`.

### Different Hotkey

Modify `hotkey_manager.py`:
```python
# Change VK_P to another key
VK_T = 0x54  # T key
# And modifiers
modifiers = MOD_CONTROL | MOD_ALT  # Ctrl+Alt instead of Ctrl+Shift
```

## License

MIT License - Use this however you want.

## Contributing

This is a personal productivity tool. Feel free to fork and customize for your needs!

---

*Built for power users who value speed over ceremony.*
