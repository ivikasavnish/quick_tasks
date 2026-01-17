# Example Configuration Files

This directory contains example configuration files for Quick Tasks.

## Local Storage (Default)

File: `settings.json`

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

With this configuration:
- Tasks are stored locally in `tasks.json`
- No authentication required
- Works offline
- Tasks only on this device

## Google Tasks Backend

File: `settings.json`

```json
{
  "start_with_windows": true,
  "hotkey": "ctrl+shift+p",
  "theme": "dark",
  "show_notifications": true,
  "overlay_width_percent": 30,
  "storage_backend": "google",
  "default_tasklist": null
}
```

Required additional file: `credentials.json` (from Google Cloud Console)

## Configuration Location

Place your `settings.json` in:
- **Linux/Mac**: `~/.config/quick_tasks/settings.json`
- **Windows**: `%APPDATA%/quick_tasks/settings.json`
