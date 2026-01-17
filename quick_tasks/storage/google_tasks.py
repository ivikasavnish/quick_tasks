"""
Google Tasks storage backend.
Wraps the Google Tasks API client as a storage backend.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from quick_tasks.storage import TaskStorageBackend
from quick_tasks.google_tasks_client import GoogleTasksClient

logger = logging.getLogger(__name__)


class GoogleTasksBackend(TaskStorageBackend):
    """
    Google Tasks storage backend.
    Uses Google Tasks API to store tasks in the cloud.
    """
    
    def __init__(self, config):
        """
        Initialize Google Tasks backend.
        
        Args:
            config: Config instance
        """
        self.config = config
        self.client = GoogleTasksClient(config)
        
    def initialize(self) -> bool:
        """Initialize Google Tasks backend."""
        try:
            return self.client.is_authenticated() or self.client.authenticate()
        except Exception as e:
            logger.error(f"Failed to initialize Google Tasks backend: {e}")
            return False
    
    def is_ready(self) -> bool:
        """Check if backend is ready."""
        return self.client.is_authenticated()
    
    def add_task(
        self,
        title: str,
        notes: Optional[str] = None,
        due: Optional[datetime] = None,
        **kwargs
    ) -> bool:
        """
        Add a task to Google Tasks.
        
        Args:
            title: Task title
            notes: Optional task notes
            due: Optional due date
            **kwargs: Additional parameters (e.g., tasklist_id)
            
        Returns:
            True if task was added successfully
        """
        tasklist_id = kwargs.get('tasklist_id')
        return self.client.add_task(title, notes, due, tasklist_id)
    
    def get_tasks(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Get tasks from Google Tasks.
        
        Args:
            **kwargs: Query parameters
            
        Returns:
            List of task dictionaries
        """
        # This would require implementing a get_tasks method in GoogleTasksClient
        # For now, return empty list
        logger.warning("Getting tasks from Google Tasks not yet implemented")
        return []
    
    @property
    def backend_name(self) -> str:
        """Get backend name."""
        return "Google Tasks"
    
    def authenticate(self) -> bool:
        """Authenticate with Google."""
        return self.client.authenticate()
    
    def clear_credentials(self):
        """Clear Google credentials."""
        self.client.clear_credentials()
