"""
Quick Tasks - Instantly add tasks to various task managers via global hotkey.

A lightweight utility for power users who value speed over ceremony.
"""

__version__ = "1.0.0"
__author__ = "Quick Tasks Contributors"

# Lazy import to avoid requiring GUI libraries for non-GUI usage
def main():
    """Entry point for the application."""
    from quick_tasks.main import main as _main
    return _main()

__all__ = ["main", "__version__"]
