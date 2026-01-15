# Quick Tasks

A lightweight Windows utility to instantly add tasks to Google Tasks using a global keyboard shortcut.

**Press `Ctrl+Shift+P` anywhere → Type your task → Press Enter → Done.**

![Quick Tasks Demo](docs/demo.gif)

## Features

- 🚀 **Instant capture**: Global hotkey works from any application
- 🎨 **Beautiful overlay**: Clean, translucent UI with Windows blur effect
- 🔒 **Secure**: OAuth 2.0 authentication, tokens stored locally
- 💨 **Fast**: Cold start under 1 second, minimal memory footprint
- 🔄 **Auto-start**: Optional Windows startup integration
- 📱 **System tray**: Runs silently in background

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Project

You need to create a Google Cloud project and enable the Tasks API:

#### Step 1: Create Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it "Quick Tasks" (or anything you prefer)
4. Click "Create"

#### Step 2: Enable Tasks API
1. Go to [APIs & Services → Library](https://console.cloud.google.com/apis/library)
2. Search for "Tasks API"
3. Click "Google Tasks API"
4. Click "Enable"

#### Step 3: Configure OAuth Consent Screen
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

#### Step 4: Create OAuth Credentials
1. Go to [APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Desktop app"
4. Name: "Quick Tasks Desktop"
5. Click "Create"
6. Click "Download JSON"
7. Rename the downloaded file to `credentials.json`
8. Place it in the `config/` folder of this project

### 3. Run the Application

```bash
python main.py
```

On first run:
1. A browser window will open for Google authentication
2. Sign in with your Google account
3. Grant access to Google Tasks
4. Close the browser when prompted
5. The app is now running in your system tray!

## Usage

| Action | Key |
|--------|-----|
| Open task input | `Ctrl+Shift+P` |
| Submit task | `Enter` |
| Cancel | `Esc` |

### System Tray Menu

Right-click the tray icon for options:
- **Re-authenticate Google**: Get new OAuth tokens
- **Start with Windows**: Enable/disable auto-start
- **Quit**: Close the application

## Building Executable

To create a standalone `.exe` file:

### Option 1: Using Build Script (Recommended)

```bash
build.bat
```

### Option 2: Manual Build

```bash
pip install pyinstaller
pyinstaller quick_tasks.spec --clean
```

The executable will be in `dist/QuickTasks.exe`.

**Important**: Copy your `config/credentials.json` to `dist/config/` before distributing.

## Project Structure

```
quick_tasks/
├── main.py              # Application entry point
├── hotkey_manager.py    # Global hotkey registration (Win32 API)
├── overlay_ui.py        # Translucent overlay UI (PySide6)
├── google_tasks_client.py # Google Tasks API client
├── tray_manager.py      # System tray icon & menu
├── startup_manager.py   # Windows auto-start registration
├── config.py            # Configuration management
├── config/
│   ├── credentials.json # OAuth client credentials (you provide)
│   ├── token.json       # OAuth tokens (auto-generated)
│   └── settings.json    # App settings (auto-generated)
└── resources/
    └── icon.ico         # Application icon (optional)
```

## Configuration

Settings are stored in `config/settings.json`:

```json
{
  "start_with_windows": false,
  "hotkey": "ctrl+shift+p",
  "theme": "dark",
  "show_notifications": true,
  "overlay_width_percent": 30
}
```

## Design Decisions

### Why PySide6?
- Native Windows blur/acrylic effect support
- Built-in system tray support (no extra dependencies)
- Better rendering than Tkinter
- MIT license (vs PyQt6's GPL)

### Why Win32 API for Hotkeys?
- Most reliable method for global hotkeys on Windows
- Works even when other apps have focus
- No polling (event-driven)
- `MOD_NOREPEAT` prevents key repeat spam

### Why Not Use `keyboard` Library?
- Requires admin/root privileges on some systems
- Uses low-level hooks that can trigger antivirus
- Less reliable with certain keyboard layouts
- We provide it as fallback if Win32 fails

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
