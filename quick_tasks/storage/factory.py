"""
Storage backend factory.
Creates and manages task storage backends.
"""

import logging
from typing import Optional
from quick_tasks.storage import TaskStorageBackend
from quick_tasks.storage.local_storage import LocalStorageBackend
from quick_tasks.storage.google_tasks import GoogleTasksBackend

logger = logging.getLogger(__name__)


class StorageFactory:
    """Factory for creating storage backends."""
    
    BACKENDS = {
        'local': LocalStorageBackend,
        'google': GoogleTasksBackend,
    }
    
    @staticmethod
    def create(backend_type: str, config) -> Optional[TaskStorageBackend]:
        """
        Create a storage backend.
        
        Args:
            backend_type: Type of backend ('local', 'google', etc.)
            config: Config instance
            
        Returns:
            Storage backend instance or None if type not found
        """
        backend_class = StorageFactory.BACKENDS.get(backend_type.lower())
        
        if not backend_class:
            logger.error(f"Unknown backend type: {backend_type}")
            return None
        
        try:
            backend = backend_class(config)
            if backend.initialize():
                logger.info(f"Initialized {backend.backend_name} backend")
                return backend
            else:
                logger.error(f"Failed to initialize {backend_type} backend")
                return None
                
        except Exception as e:
            logger.error(f"Error creating {backend_type} backend: {e}")
            return None
    
    @staticmethod
    def list_backends() -> list:
        """
        Get list of available backend types.
        
        Returns:
            List of backend type names
        """
        return list(StorageFactory.BACKENDS.keys())
