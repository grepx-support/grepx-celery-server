"""Task registry for managing task definitions."""

import importlib
from typing import List, Optional, Callable, Any, Dict
from dataclasses import dataclass, field


@dataclass
class TaskDefinition:
    """Definition of a Celery task."""

    name: str
    module_path: str
    function_name: str
    description: str = ""
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def load_function(self) -> Callable:
        """Load the task function from module."""
        try:
            module = importlib.import_module(self.module_path)
            func = getattr(module, self.function_name)
            if not callable(func):
                raise ValueError(
                    f"{self.module_path}.{self.function_name} is not callable"
                )
            return func
        except ImportError as e:
            raise ImportError(
                f"Failed to import module {self.module_path}: {e}"
            )
        except AttributeError as e:
            raise AttributeError(
                f"Function {self.function_name} not found in {self.module_path}: {e}"
            )


class TaskRegistry:
    """Registry for task definitions."""

    def __init__(self):
        self._tasks: Dict[str, TaskDefinition] = {}

    def register(self, task_def: TaskDefinition) -> None:
        """Register a task definition."""
        if task_def.name in self._tasks:
            raise ValueError(f"Task {task_def.name} already registered")
        self._tasks[task_def.name] = task_def

    def get(self, name: str) -> Optional[TaskDefinition]:
        """Get a task definition by name."""
        return self._tasks.get(name)

    def filter(
        self,
        enabled: Optional[bool] = None,
        tags: Optional[List[str]] = None,
    ) -> List[TaskDefinition]:
        """Filter tasks by criteria."""
        results = list(self._tasks.values())

        if enabled is not None:
            results = [t for t in results if t.enabled == enabled]

        if tags:
            results = [
                t for t in results if any(tag in t.tags for tag in tags)
            ]

        return results

    def list_all(self) -> List[TaskDefinition]:
        """List all registered tasks."""
        return list(self._tasks.values())

    def clear(self) -> None:
        """Clear all registered tasks."""
        self._tasks.clear()

