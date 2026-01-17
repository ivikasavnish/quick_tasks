"""
Google Tasks API client.
Handles OAuth 2.0 authentication and task creation.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Google API scopes
SCOPES = ['https://www.googleapis.com/auth/tasks']


class GoogleTasksClient:
    """
    Client for Google Tasks API with OAuth 2.0 authentication.
    Handles token storage, refresh, and task operations.
    """
    
    def __init__(self, config):
        """
        Initialize the client.
        
        Args:
            config: Config instance for storing credentials
        """
        self.config = config
        self._credentials = None
        self._service = None
        self._default_tasklist_id = None
        
    @property
    def credentials_path(self) -> Path:
        """Path to OAuth client credentials file."""
        return self.config.config_dir / "credentials.json"
        
    @property
    def token_path(self) -> Path:
        """Path to stored access token."""
        return self.config.config_dir / "token.json"
        
    def is_authenticated(self) -> bool:
        """Check if valid credentials exist."""
        if self._credentials and self._credentials.valid:
            return True
            
        return self._load_credentials()
        
    def authenticate(self, force_new: bool = False) -> bool:
        """
        Authenticate with Google.
        
        Args:
            force_new: Force new authentication even if token exists
            
        Returns:
            True if authentication successful
        """
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            
            creds = None
            
            # Load existing token if not forcing new
            if not force_new and self.token_path.exists():
                try:
                    creds = Credentials.from_authorized_user_file(
                        str(self.token_path), SCOPES
                    )
                except Exception as e:
                    logger.warning(f"Failed to load token: {e}")
                    
            # Refresh or get new credentials
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None
                    
            if not creds or not creds.valid:
                if not self.credentials_path.exists():
                    logger.error("credentials.json not found")
                    return False
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(
                    port=0,
                    success_message="Authentication successful! You can close this window.",
                    open_browser=True
                )
                
            # Save credentials
            self._save_credentials(creds)
            self._credentials = creds
            self._service = None  # Reset service to use new creds
            
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
            
    def clear_credentials(self):
        """Clear stored credentials."""
        if self.token_path.exists():
            self.token_path.unlink()
        self._credentials = None
        self._service = None
        
    def _load_credentials(self) -> bool:
        """Load credentials from storage."""
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            
            if not self.token_path.exists():
                return False
                
            creds = Credentials.from_authorized_user_file(
                str(self.token_path), SCOPES
            )
            
            # Refresh if expired
            if creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self._save_credentials(creds)
                except Exception:
                    return False
                    
            if creds.valid:
                self._credentials = creds
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"Failed to load credentials: {e}")
            return False
            
    def _save_credentials(self, creds):
        """Save credentials to storage."""
        try:
            self.config.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            
    def _get_service(self):
        """Get or create the Tasks API service."""
        if self._service:
            return self._service
            
        if not self._credentials:
            if not self._load_credentials():
                if not self.authenticate():
                    raise RuntimeError("Not authenticated")
                    
        try:
            from googleapiclient.discovery import build
            
            self._service = build(
                'tasks', 'v1',
                credentials=self._credentials,
                cache_discovery=False
            )
            return self._service
            
        except Exception as e:
            logger.error(f"Failed to create service: {e}")
            raise
            
    def _get_default_tasklist(self) -> str:
        """Get the default task list ID."""
        if self._default_tasklist_id:
            return self._default_tasklist_id
            
        try:
            service = self._get_service()
            results = service.tasklists().list(maxResults=1).execute()
            tasklists = results.get('items', [])
            
            if tasklists:
                self._default_tasklist_id = tasklists[0]['id']
                return self._default_tasklist_id
            else:
                raise RuntimeError("No task lists found")
                
        except Exception as e:
            logger.error(f"Failed to get default task list: {e}")
            raise
            
    def get_tasklists(self) -> List[Dict[str, str]]:
        """Get all task lists."""
        try:
            service = self._get_service()
            results = service.tasklists().list(maxResults=100).execute()
            return results.get('items', [])
        except Exception as e:
            logger.error(f"Failed to get task lists: {e}")
            return []
            
    def add_task(
        self,
        title: str,
        notes: str = None,
        due: datetime = None,
        tasklist_id: str = None
    ) -> bool:
        """
        Add a new task to Google Tasks.
        
        Args:
            title: Task title
            notes: Optional task notes
            due: Optional due date
            tasklist_id: Optional specific task list ID
            
        Returns:
            True if task was added successfully
        """
        try:
            service = self._get_service()
            
            if not tasklist_id:
                tasklist_id = self._get_default_tasklist()
                
            task_body = {'title': title}
            
            if notes:
                task_body['notes'] = notes
                
            if due:
                # Google Tasks API expects RFC 3339 format
                task_body['due'] = due.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                
            service.tasks().insert(
                tasklist=tasklist_id,
                body=task_body
            ).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add task: {type(e).__name__}")
            return False
            

class DateParser:
    """
    Natural language date parser for task due dates.
    Supports phrases like "tomorrow", "next monday", "in 3 days".
    """
    
    @staticmethod
    def parse(text: str) -> Optional[datetime]:
        """
        Parse natural language date from text.
        
        Args:
            text: Text potentially containing a date reference
            
        Returns:
            Parsed datetime or None
        """
        try:
            # Try dateparser if available
            import dateparser
            
            settings = {
                'PREFER_DATES_FROM': 'future',
                'PREFER_DAY_OF_MONTH': 'first',
                'RETURN_AS_TIMEZONE_AWARE': False
            }
            
            result = dateparser.parse(text, settings=settings)
            return result
            
        except ImportError:
            # Fallback to basic parsing
            return DateParser._basic_parse(text)
        except Exception:
            return None
            
    @staticmethod
    def _basic_parse(text: str) -> Optional[datetime]:
        """Basic date parsing without external libraries."""
        from datetime import timedelta
        
        text = text.lower()
        now = datetime.now()
        
        if 'today' in text:
            return now.replace(hour=23, minute=59, second=0)
        elif 'tomorrow' in text:
            return (now + timedelta(days=1)).replace(hour=23, minute=59, second=0)
        elif 'next week' in text:
            return (now + timedelta(weeks=1)).replace(hour=23, minute=59, second=0)
            
        return None
