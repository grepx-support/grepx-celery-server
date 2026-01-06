"""Framework-agnostic task registry."""

import logging
from typing import Dict, Optional, List, Set
from .task_definition import TaskDefinition

logger = logging.getLogger(__name__)


class TaskRegistry:
    """Central registry for task definitions."""

    def __init__(self):
        self._tasks: Dict[str, TaskDefinition] = {}
        self._tag_index: Dict[str, Set[str]] = {}

    def register(self, task_def: TaskDefinition) -> None:
        """Register a task definition."""
        if task_def.name in self._tasks:
            logger.warning(f"Task {task_def.name} already registered, overwriting")
            self._remove_from_tag_index(task_def.name)

        self._tasks[task_def.name] = task_def
        self._add_to_tag_index(task_def)
        logger.info(f"✓ Registered task: {task_def.name}")

    def unregister(self, name: str) -> bool:
        """Unregister a task."""
        if name in self._tasks:
            self._remove_from_tag_index(name)
            del self._tasks[name]
            logger.info(f"✓ Unregistered task: {name}")
            return True
        return False

    def get(self, name: str) -> Optional[TaskDefinition]:
        """Get task definition by name."""
        return self._tasks.get(name)

    def all(self) -> Dict[str, TaskDefinition]:
        """Get all task definitions."""
        return self._tasks.copy()

    def filter(
        self,
        enabled: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        module_path: Optional[str] = None,
    ) -> List[TaskDefinition]:
        """Filter tasks by criteria."""
        tasks = list(self._tasks.values())

        if enabled is not None:
            tasks = [t for t in tasks if t.enabled == enabled]

        if tags:
            matching_names = set()
            for tag in tags:
                matching_names.update(self._tag_index.get(tag, set()))
            tasks = [t for t in tasks if t.name in matching_names]

        if module_path:
            tasks = [t for t in tasks if t.module_path == module_path]

        return tasks

    def list_names(self) -> List[str]:
        """List all task names."""
        return sorted(self._tasks.keys())

    def list_tags(self) -> List[str]:
        """List all unique tags."""
        return sorted(self._tag_index.keys())

    def _add_to_tag_index(self, task_def: TaskDefinition) -> None:
        """Add task to tag index."""
        for tag in task_def.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(task_def.name)

    def _remove_from_tag_index(self, name: str) -> None:
        """Remove task from tag index."""
        task_def = self._tasks.get(name)
        if task_def:
            for tag in task_def.tags:
                if tag in self._tag_index:
                    self._tag_index[tag].discard(name)
                    if not self._tag_index[tag]:
                        del self._tag_index[tag]

    def clear(self) -> None:
        """Clear all tasks."""
        self._tasks.clear()
        self._tag_index.clear()
        logger.info("✓ Cleared all tasks")

    def __len__(self) -> int:
        return len(self._tasks)

    def __contains__(self, name: str) -> bool:
        return name in self._tasks

    def __repr__(self) -> str:
        return f"<TaskRegistry: {len(self)} task(s)>"

