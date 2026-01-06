"""SQLite storage helper."""

import sqlite3
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SQLiteStorage:
    """Helper for managing tasks in SQLite database."""

    def __init__(self, db_path: str, table: str = "tasks"):
        self.db_path = db_path
        self.table = table
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                module_path TEXT NOT NULL,
                function_name TEXT NOT NULL,
                description TEXT,
                enabled INTEGER DEFAULT 1,
                options TEXT,
                tags TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()
        conn.close()
        logger.info(f"✓ SQLite database initialized: {self.db_path}")

    def add_task(
        self,
        name: str,
        module_path: str,
        function_name: str,
        description: str = "",
        enabled: bool = True,
        options: Dict[str, Any] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> bool:
        """Add a task to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"""
                INSERT INTO {self.table}
                (name, module_path, function_name, description, enabled, options, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    name,
                    module_path,
                    function_name,
                    description,
                    1 if enabled else 0,
                    json.dumps(options) if options else None,
                    json.dumps(tags) if tags else None,
                    json.dumps(metadata) if metadata else None,
                ),
            )
            conn.commit()
            logger.info(f"✓ Added task: {name}")
            return True
        except sqlite3.IntegrityError:
            logger.error(f"✗ Task already exists: {name}")
            return False
        finally:
            conn.close()

    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tasks."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table}")
        rows = cursor.fetchall()
        tasks = [dict(row) for row in rows]
        conn.close()
        return tasks

    def enable_task(self, name: str) -> bool:
        """Enable a task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE {self.table} SET enabled = 1, updated_at = ? WHERE name = ?",
            (datetime.utcnow(), name),
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        if success:
            logger.info(f"✓ Enabled task: {name}")
        return success

    def disable_task(self, name: str) -> bool:
        """Disable a task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE {self.table} SET enabled = 0, updated_at = ? WHERE name = ?",
            (datetime.utcnow(), name),
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        if success:
            logger.info(f"✓ Disabled task: {name}")
        return success

    def delete_task(self, name: str) -> bool:
        """Delete a task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {self.table} WHERE name = ?", (name,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        if success:
            logger.info(f"✓ Deleted task: {name}")
        return success

