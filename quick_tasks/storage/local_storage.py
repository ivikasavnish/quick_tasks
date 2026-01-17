"""
Local JSON file storage backend.
Stores tasks in a local JSON file - no cloud required.
"""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from quick_tasks.storage import TaskStorageBackend

logger = logging.getLogger(__name__)


class LocalStorageBackend(TaskStorageBackend):
    """
    Local JSON file storage backend.
    Stores tasks in a simple JSON file in the config directory.
    """
    
    def __init__(self, config):
        """
        Initialize local storage backend.
        
        Args:
            config: Config instance
        """
        self.config = config
        self.tasks_file = config.config_dir / "tasks.json"
        self._tasks = []
        
    def initialize(self) -> bool:
        """Initialize local storage."""
        try:
            self.config.config_dir.mkdir(parents=True, exist_ok=True)
            
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r') as f:
                    self._tasks = json.load(f)
            else:
                self._tasks = []
                self._save()
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize local storage: {e}")
            return False
    
    def is_ready(self) -> bool:
        """Check if backend is ready."""
        return self.tasks_file.exists()
    
    def add_task(
        self,
        title: str,
        notes: Optional[str] = None,
        due: Optional[datetime] = None,
        **kwargs
    ) -> bool:
        """
        Add a task to local storage.
        
        Args:
            title: Task title
            notes: Optional task notes
            due: Optional due date
            **kwargs: Additional fields
            
        Returns:
            True if task was added successfully
        """
        try:
            task = {
                'id': self._generate_id(),
                'title': title,
                'notes': notes,
                'due': due.isoformat() if due else None,
                'completed': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
            }
            
            # Add any additional fields
            for key, value in kwargs.items():
                if key not in task:
                    task[key] = value
            
            self._tasks.append(task)
            self._save()
            
            logger.info(f"Task added to local storage (total: {len(self._tasks)})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add task to local storage: {e}")
            return False
    
    def get_tasks(self, completed: bool = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Get tasks from local storage.
        
        Args:
            completed: Filter by completion status (None = all)
            **kwargs: Additional filter parameters
            
        Returns:
            List of task dictionaries
        """
        try:
            if not self.tasks_file.exists():
                return []
            
            tasks = self._tasks.copy()
            
            # Filter by completion status
            if completed is not None:
                tasks = [t for t in tasks if t.get('completed') == completed]
            
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to get tasks from local storage: {e}")
            return []
    
    @property
    def backend_name(self) -> str:
        """Get backend name."""
        return "Local Storage"
    
    def _generate_id(self) -> str:
        """Generate a unique task ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _save(self):
        """Save tasks to file."""
        try:
            with open(self.tasks_file, 'w') as f:
                json.dump(self._tasks, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save tasks: {e}")
