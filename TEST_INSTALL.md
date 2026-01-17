# Installation and Testing Guide

This guide helps you test the Quick Tasks package before publishing.

## Local Installation Test

### 1. Build the Package

```bash
cd /path/to/quick_tasks
python -m build
```

### 2. Create Test Environment

```bash
# Create a clean virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
```

### 3. Install from Local Build

```bash
pip install dist/quick_tasks-1.0.0-py3-none-any.whl
```

### 4. Verify Installation

```bash
# Check if command is available
which quick-tasks  # On Windows: where quick-tasks

# Test imports
python -c "from quick_tasks import __version__; print(f'Version: {__version__}')"
python -c "from quick_tasks.storage.factory import StorageFactory; print('Backends:', StorageFactory.list_backends())"
```

### 5. Test Local Storage Backend

```bash
# This will fail on headless systems without display, but tests imports
python << 'PYTHON'
from quick_tasks.storage.local_storage import LocalStorageBackend
from quick_tasks.config import Config
from pathlib import Path
import tempfile

# Create temp config dir
with tempfile.TemporaryDirectory() as tmpdir:
    config = Config(Path(tmpdir))
    backend = LocalStorageBackend(config)
    
    # Initialize
    assert backend.initialize(), "Failed to initialize backend"
    assert backend.is_ready(), "Backend not ready"
    
    # Add a task
    assert backend.add_task("Test task", notes="Test notes"), "Failed to add task"
    
    # Get tasks
    tasks = backend.get_tasks()
    assert len(tasks) == 1, f"Expected 1 task, got {len(tasks)}"
    assert tasks[0]['title'] == "Test task", "Task title mismatch"
    
    print("✓ Local storage backend working correctly")
PYTHON
```

## Platform-Specific Tests

### Linux/Ubuntu

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

# Test installation
python3 -m venv test_env
source test_env/bin/activate
pip install dist/quick_tasks-1.0.0-py3-none-any.whl

# Note: GUI features require X11 or Wayland
```

### macOS

```bash
# Install Python if needed
brew install python3

# Test installation
python3 -m venv test_env
source test_env/bin/activate
pip install dist/quick_tasks-1.0.0-py3-none-any.whl

# Note: May need to grant accessibility permissions
```

### Windows

```powershell
# Test installation
python -m venv test_env
test_env\Scripts\activate
pip install dist\quick_tasks-1.0.0-py3-none-any.whl

# Test command
quick-tasks
```

## Integration Tests

### Test Configuration

```python
from quick_tasks.config import Config
from pathlib import Path
import tempfile
import json

with tempfile.TemporaryDirectory() as tmpdir:
    config = Config(Path(tmpdir))
    
    # Test default config
    assert config.get('storage_backend') == 'local'
    assert config.get('hotkey') == 'ctrl+shift+p'
    
    # Test set/get
    config.set('test_key', 'test_value')
    assert config.get('test_key') == 'test_value'
    
    # Verify file was created
    settings_file = Path(tmpdir) / 'settings.json'
    assert settings_file.exists()
    
    print("✓ Configuration working correctly")
```

### Test Storage Factory

```python
from quick_tasks.storage.factory import StorageFactory
from quick_tasks.config import Config
from pathlib import Path
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    config = Config(Path(tmpdir))
    
    # Test local backend
    backend = StorageFactory.create('local', config)
    assert backend is not None
    assert backend.backend_name == 'Local Storage'
    
    # Test listing backends
    backends = StorageFactory.list_backends()
    assert 'local' in backends
    assert 'google' in backends
    
    print("✓ Storage factory working correctly")
```

## Expected Behavior

### On First Run

1. **Configuration Created**: `~/.config/quick_tasks/settings.json` (Linux/Mac)
2. **Default Backend**: Local storage (no authentication needed)
3. **System Tray**: Icon appears in system tray
4. **Hotkey Registered**: `Ctrl+Shift+P` ready to use

### Using Local Storage

- **Tasks File**: `~/.config/quick_tasks/tasks.json`
- **No Authentication**: Works immediately
- **Offline**: Fully functional offline

### Using Google Tasks

- **Requires Setup**: OAuth credentials needed
- **First Auth**: Browser opens for authentication
- **Token Storage**: `~/.config/quick_tasks/token.json`

## Troubleshooting

### Import Errors

```python
# Test if all modules import correctly
import quick_tasks
import quick_tasks.storage
import quick_tasks.storage.factory
import quick_tasks.storage.local_storage
import quick_tasks.storage.google_tasks
print("✓ All imports successful")
```

### Display Issues

On headless systems, GUI components will fail. This is expected.

To test without GUI:
```python
# Test only backend logic
from quick_tasks.storage.local_storage import LocalStorageBackend
# ... run backend tests
```

### Permission Issues

- **macOS**: Grant accessibility permissions in System Preferences
- **Linux**: Ensure user has access to X11/Wayland session

## Clean Up

```bash
# Deactivate and remove test environment
deactivate
rm -rf test_env

# Remove test config
rm -rf ~/.config/quick_tasks  # Linux/Mac
# or
rmdir /s %APPDATA%\quick_tasks  # Windows
```

## Next Steps

After successful local testing:
1. Test on TestPyPI
2. Test installation from TestPyPI
3. Publish to PyPI
4. Test installation from PyPI

See [PUBLISHING.md](PUBLISHING.md) for publishing instructions.
