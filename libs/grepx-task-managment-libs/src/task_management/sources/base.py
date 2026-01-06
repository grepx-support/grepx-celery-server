"""Abstract task source."""

from abc import ABC, abstractmethod
from typing import List
from ..core.task_definition import TaskDefinition


class TaskSource(ABC):
    """Abstract base class for task sources."""

    @abstractmethod
    def load_tasks(self) -> List[TaskDefinition]:
        """
        Load task definitions from source.

        Returns:
            List of TaskDefinition objects
        """
        pass

    @abstractmethod
    def save_task(self, task_def: TaskDefinition) -> bool:
        """
        Save a task definition to source.

        Args:
            task_def: Task definition to save

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def delete_task(self, name: str) -> bool:
        """
        Delete a task from source.

        Args:
            name: Task name

        Returns:
            True if successful
        """
        pass

