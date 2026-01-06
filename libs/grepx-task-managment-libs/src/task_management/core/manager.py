"""Task manager for CRUD operations."""

import logging
from typing import List, Optional
from .task_definition import TaskDefinition
from .task_registry import TaskRegistry
from ..sources.base import TaskSource

logger = logging.getLogger(__name__)


class TaskManager:
    """Manage task definitions with CRUD operations."""

    def __init__(self, registry: TaskRegistry):
        self.registry = registry

    def load_from_source(self, source: TaskSource) -> int:
        """
        Load tasks from a source into registry.

        Returns:
            Number of tasks loaded
        """
        tasks = source.load_tasks()
        for task_def in tasks:
            self.registry.register(task_def)

        logger.info(f"✓ Loaded {len(tasks)} tasks from source")
        return len(tasks)

    def create_task(self, task_def: TaskDefinition) -> None:
        """Create a new task."""
        self.registry.register(task_def)

    def get_task(self, name: str) -> Optional[TaskDefinition]:
        """Get task by name."""
        return self.registry.get(name)

    def list_tasks(
        self,
        enabled: Optional[bool] = None,
        tags: Optional[List[str]] = None,
    ) -> List[TaskDefinition]:
        """List tasks with filters."""
        return self.registry.filter(enabled=enabled, tags=tags)

    def update_task(self, name: str, **updates) -> bool:
        """Update task definition."""
        task_def = self.registry.get(name)
        if not task_def:
            return False
        for key, value in updates.items():
            if hasattr(task_def, key):
                setattr(task_def, key, value)
        return True

    def delete_task(self, name: str) -> bool:
        """Delete task."""
        return self.registry.unregister(name)

    def count(self) -> int:
        """Get total number of tasks."""
        return len(self.registry)

