"""Database-based task source."""

import json
import logging
import sqlite3
from typing import List
from pathlib import Path

from ..registry import TaskDefinition

logger = logging.getLogger(__name__)


class DatabaseTaskSource:
    """Load tasks from database."""

    def __init__(self, db_uri: str, table: str = "tasks"):
        """
        Initialize database source.

        Args:
            db_uri: Database URI (e.g., 'sqlite:///tasks.db' or 'sqlite:///path/to/tasks.db')
            table: Table name containing tasks
        """
        self.db_uri = db_uri
        self.table = table

    def _get_sqlite_path(self) -> Path:
        """Extract SQLite database path from URI."""
        if self.db_uri.startswith("sqlite:///"):
            # Remove 'sqlite:///' prefix
            db_path = self.db_uri.replace("sqlite:///", "", 1)
            return Path(db_path)
        elif self.db_uri.startswith("sqlite://"):
            # Handle 'sqlite://' (absolute path)
            db_path = self.db_uri.replace("sqlite://", "", 1)
            return Path(db_path)
        else:
            raise ValueError(f"Unsupported database URI format: {self.db_uri}. Only SQLite is supported.")

    def load_tasks(self) -> List[TaskDefinition]:
        """Load tasks from database."""
        db_path = self._get_sqlite_path()
        
        if not db_path.exists():
            logger.warning(f"Database file not found: {db_path}")
            return []

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()

        try:
            cursor.execute(f"SELECT * FROM {self.table}")
            rows = cursor.fetchall()
            
            task_definitions = []
            
            for row in rows:
                try:
                    # Convert row to dictionary
                    row_dict = dict(row)
                    
                    # Parse options and metadata if they're strings (JSON)
                    options = row_dict.get("options", {})
                    if isinstance(options, str):
                        options = json.loads(options) if options else {}
                    
                    metadata = row_dict.get("metadata", {})
                    if isinstance(metadata, str):
                        metadata = json.loads(metadata) if metadata else {}
                    
                    # Parse tags if it's a string
                    tags = row_dict.get("tags", [])
                    if isinstance(tags, str):
                        tags = json.loads(tags) if tags else []
                    
                    task_def = TaskDefinition(
                        name=row_dict["name"],
                        module_path=row_dict["module_path"],
                        function_name=row_dict["function_name"],
                        description=row_dict.get("description", ""),
                        enabled=bool(row_dict.get("enabled", True)),
                        tags=tags,
                        options=options,
                        metadata=metadata,
                    )
                    task_definitions.append(task_def)
                except (KeyError, ValueError, json.JSONDecodeError) as e:
                    logger.warning(f"Skipping invalid task row: {e}")
                    continue

            return task_definitions
        finally:
            conn.close()

