"""SQLite storage for tasks."""

import json
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path


class SQLiteStorage:
    """SQLite storage for task definitions."""

    def __init__(self, db_path: str):
        """
        Initialize SQLite storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                module_path TEXT NOT NULL,
                function_name TEXT NOT NULL,
                description TEXT,
                enabled INTEGER DEFAULT 1,
                tags TEXT,
                options TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_task(
        self,
        name: str,
        module_path: str,
        function_name: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        enabled: bool = True,
    ) -> None:
        """Add a task to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        tags_json = json.dumps(tags or [])
        options_json = json.dumps(options or {})
        metadata_json = json.dumps(metadata or {})

        cursor.execute("""
            INSERT OR REPLACE INTO tasks 
            (name, module_path, function_name, description, enabled, tags, options, metadata, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            name,
            module_path,
            function_name,
            description,
            1 if enabled else 0,
            tags_json,
            options_json,
            metadata_json,
        ))

        conn.commit()
        conn.close()

    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tasks."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        tasks = []
        for row in rows:
            task_dict = dict(zip(columns, row))
            # Parse JSON fields
            if task_dict.get("tags"):
                task_dict["tags"] = json.loads(task_dict["tags"])
            if task_dict.get("options"):
                task_dict["options"] = json.loads(task_dict["options"])
            if task_dict.get("metadata"):
                task_dict["metadata"] = json.loads(task_dict["metadata"])
            tasks.append(task_dict)

        conn.close()
        return tasks

    def get_task(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a task by name."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE name = ?", (name,))
        row = cursor.fetchone()

        if row is None:
            conn.close()
            return None

        columns = [description[0] for description in cursor.description]
        task_dict = dict(zip(columns, row))

        # Parse JSON fields
        if task_dict.get("tags"):
            task_dict["tags"] = json.loads(task_dict["tags"])
        if task_dict.get("options"):
            task_dict["options"] = json.loads(task_dict["options"])
        if task_dict.get("metadata"):
            task_dict["metadata"] = json.loads(task_dict["metadata"])

        conn.close()
        return task_dict

    def delete_task(self, name: str) -> bool:
        """Delete a task by name."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tasks WHERE name = ?", (name,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()
        return deleted

