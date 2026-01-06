"""Config-based task source."""

import logging
from typing import Dict, Any, List

from ..registry import TaskDefinition

logger = logging.getLogger(__name__)


class ConfigTaskSource:
    """Load tasks from configuration dictionary."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize config source.

        Args:
            config: Configuration dictionary with 'tasks' key containing task list
        """
        self.config = config

    def load_tasks(self) -> List[TaskDefinition]:
        """Load tasks from configuration."""
        tasks = self.config.get("tasks", [])
        task_definitions = []

        for task_data in tasks:
            try:
                task_def = TaskDefinition(
                    name=task_data["name"],
                    module_path=task_data["module_path"],
                    function_name=task_data["function_name"],
                    description=task_data.get("description", ""),
                    enabled=task_data.get("enabled", True),
                    tags=task_data.get("tags", []),
                    options=task_data.get("options", {}),
                    metadata=task_data.get("metadata", {}),
                )
                task_definitions.append(task_def)
            except KeyError as e:
                logger.warning(f"Skipping invalid task definition: missing {e}")
                continue

        return task_definitions

