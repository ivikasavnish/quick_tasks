"""
Abstract base class for task storage backends.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime


class TaskStorageBackend(ABC):
    """
    Abstract interface for task storage backends.
    All storage backends must implement these methods.
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the storage backend.
        
        Returns:
            True if initialization was successful
        """
        pass
    
    @abstractmethod
    def is_ready(self) -> bool:
        """
        Check if the backend is ready to accept tasks.
        
        Returns:
            True if backend is ready
        """
        pass
    
    @abstractmethod
    def add_task(
        self,
        title: str,
        notes: Optional[str] = None,
        due: Optional[datetime] = None,
        **kwargs
    ) -> bool:
        """
        Add a new task.
        
        Args:
            title: Task title
            notes: Optional task notes/description
            due: Optional due date
            **kwargs: Backend-specific additional parameters
            
        Returns:
            True if task was added successfully
        """
        pass
    
    @abstractmethod
    def get_tasks(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Get tasks from storage.
        
        Args:
            **kwargs: Backend-specific query parameters
            
        Returns:
            List of task dictionaries
        """
        pass
    
    @property
    @abstractmethod
    def backend_name(self) -> str:
        """
        Get the name of this backend.
        
        Returns:
            Backend name
        """
        pass
    
    def authenticate(self) -> bool:
        """
        Authenticate with the backend (if required).
        
        Returns:
            True if authentication successful
        """
        return True
    
    def clear_credentials(self):
        """Clear stored credentials (if applicable)."""
        pass
