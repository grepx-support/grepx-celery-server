"""Task manager for loading tasks from various sources."""

import logging
from typing import Protocol

from .registry import TaskRegistry, TaskDefinition

logger = logging.getLogger(__name__)


class TaskSource(Protocol):
    """Protocol for task sources."""

    def load_tasks(self) -> list[TaskDefinition]:
        """Load tasks from source."""
        ...


class TaskManager:
    """Manages task loading and registration."""

    def __init__(self, registry: TaskRegistry):
        self.registry = registry

    def load_from_source(self, source: TaskSource) -> None:
        """Load tasks from a source and register them."""
        try:
            tasks = source.load_tasks()
            logger.info(f"Loaded {len(tasks)} tasks from source")

            for task_def in tasks:
                try:
                    self.registry.register(task_def)
                    logger.debug(f"Registered task: {task_def.name}")
                except ValueError as e:
                    logger.warning(f"Failed to register task {task_def.name}: {e}")

        except Exception as e:
            logger.error(f"Failed to load tasks from source: {e}")
            raise

