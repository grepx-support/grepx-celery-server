"""Database task source."""

import json
import logging
from typing import List
from datetime import datetime
from .base import TaskSource
from ..core.task_definition import TaskDefinition

logger = logging.getLogger(__name__)


class DatabaseTaskSource(TaskSource):
    """Load tasks from database using SQLAlchemy."""

    def __init__(self, db_uri: str, table: str = "tasks"):
        self.db_uri = db_uri
        self.table = table
        self._engine = None
        self._table = None
        self._init_db()

    def _init_db(self):
        """Initialize database connection and table."""
        try:
            from sqlalchemy import (
                create_engine,
                Table,
                Column,
                Integer,
                String,
                Boolean,
                Text,
                DateTime,
                MetaData,
            )

            self._engine = create_engine(self.db_uri)
            metadata = MetaData()

            self._table = Table(
                self.table,
                metadata,
                Column("id", Integer, primary_key=True, autoincrement=True),
                Column("name", String(255), unique=True, nullable=False),
                Column("module_path", String(255), nullable=False),
                Column("function_name", String(255), nullable=False),
                Column("description", Text),
                Column("enabled", Boolean, default=True),
                Column("options", Text),
                Column("tags", Text),
                Column("metadata", Text),
                Column("created_at", DateTime, default=datetime.utcnow),
                Column(
                    "updated_at",
                    DateTime,
                    default=datetime.utcnow,
                    onupdate=datetime.utcnow,
                ),
            )

            metadata.create_all(self._engine)
            logger.info(f"✓ Database initialized: {self.db_uri}")
        except ImportError:
            logger.error(
                "SQLAlchemy not installed. Install with: pip install task-management[database]"
            )
            raise

    def load_tasks(self) -> List[TaskDefinition]:
        """Load tasks from database."""
        from sqlalchemy import select

        tasks = []
        try:
            with self._engine.connect() as conn:
                result = conn.execute(
                    select(self._table).where(self._table.c.enabled == True)
                )
                for row in result:
                    task_def = TaskDefinition(
                        name=row.name,
                        module_path=row.module_path,
                        function_name=row.function_name,
                        description=row.description or "",
                        enabled=bool(row.enabled),
                        options=json.loads(row.options) if row.options else {},
                        tags=json.loads(row.tags) if row.tags else [],
                        metadata=json.loads(row.metadata) if row.metadata else {},
                        created_at=row.created_at,
                        updated_at=row.updated_at,
                    )
                    tasks.append(task_def)
            logger.info(f"✓ Loaded {len(tasks)} tasks from database")
        except Exception as e:
            logger.error(f"✗ Failed to load tasks from database: {e}")
        return tasks

    def save_task(self, task_def: TaskDefinition) -> bool:
        """Save task to database."""
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert

        try:
            with self._engine.begin() as conn:
                stmt = sqlite_insert(self._table).values(
                    name=task_def.name,
                    module_path=task_def.module_path,
                    function_name=task_def.function_name,
                    description=task_def.description,
                    enabled=task_def.enabled,
                    options=json.dumps(task_def.options),
                    tags=json.dumps(task_def.tags),
                    metadata=json.dumps(task_def.metadata),
                )

                stmt = stmt.on_conflict_do_update(
                    index_elements=["name"],
                    set_=dict(
                        module_path=task_def.module_path,
                        function_name=task_def.function_name,
                        description=task_def.description,
                        enabled=task_def.enabled,
                        options=json.dumps(task_def.options),
                        tags=json.dumps(task_def.tags),
                        metadata=json.dumps(task_def.metadata),
                        updated_at=datetime.utcnow(),
                    ),
                )

                conn.execute(stmt)

            logger.info(f"✓ Saved task: {task_def.name}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to save task {task_def.name}: {e}")
            return False

    def delete_task(self, name: str) -> bool:
        """Delete task from database."""
        from sqlalchemy import delete

        try:
            with self._engine.begin() as conn:
                stmt = delete(self._table).where(self._table.c.name == name)
                result = conn.execute(stmt)

            if result.rowcount > 0:
                logger.info(f"✓ Deleted task: {name}")
                return True
            else:
                logger.warning(f"Task not found: {name}")
                return False
        except Exception as e:
            logger.error(f"✗ Failed to delete task {name}: {e}")
            return False

