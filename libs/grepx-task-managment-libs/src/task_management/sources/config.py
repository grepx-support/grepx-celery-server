"""Configuration-based task source."""

import logging
from typing import List, Dict, Any
from .base import TaskSource
from ..core.task_definition import TaskDefinition

logger = logging.getLogger(__name__)


class ConfigTaskSource(TaskSource):
    """Load tasks from configuration dictionary."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize config source.

        Args:
            config: Configuration dictionary with 'tasks' key
        """
        self.config = config

    def load_tasks(self) -> List[TaskDefinition]:
        """Load tasks from config."""
        tasks = []
        if "tasks" not in self.config:
            logger.warning("No 'tasks' key in configuration")
            return tasks

        for task_cfg in self.config["tasks"]:
            try:
                task_def = TaskDefinition(
                    name=task_cfg["name"],
                    module_path=task_cfg["module_path"],
                    function_name=task_cfg["function_name"],
                    description=task_cfg.get("description", ""),
                    enabled=task_cfg.get("enabled", True),
                    options=task_cfg.get("options", {}),
                    tags=task_cfg.get("tags", []),
                    metadata=task_cfg.get("metadata", {}),
                )
                tasks.append(task_def)
            except KeyError as e:
                logger.error(f"Missing required field in task config: {e}")
            except Exception as e:
                logger.error(f"Error loading task from config: {e}")

        logger.info(f"✓ Loaded {len(tasks)} tasks from config")
        return tasks

    def save_task(self, task_def: TaskDefinition) -> bool:
        """Config source is read-only."""
        logger.warning("ConfigTaskSource is read-only")
        return False

    def delete_task(self, name: str) -> bool:
        """Config source is read-only."""
        logger.warning("ConfigTaskSource is read-only")
        return False

