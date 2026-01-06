import logging
from typing import Dict, Any

from celery import Celery
from task_management import TaskRegistry, TaskDefinition

logger = logging.getLogger(__name__)


class CeleryTaskAdapter:
    """Adapter to register tasks with Celery."""

    def __init__(self, celery_app: Celery, registry: TaskRegistry):
        self.celery_app = celery_app
        self.registry = registry
        self._celery_tasks: Dict[str, Any] = {}

    def register_all(self) -> None:
        """Register all enabled tasks with Celery."""
        logger.info("Registering tasks with Celery...")

        for task_def in self.registry.filter(enabled=True):
            self.register_task(task_def)

        logger.info(f"✓ Registered {len(self._celery_tasks)} Celery tasks")

    def register_task(self, task_def: TaskDefinition) -> bool:
        """Register a single task with Celery."""
        try:
            func = task_def.load_function()

            celery_task = self.celery_app.task(
                name=task_def.name, **task_def.options
            )(func)

            self._celery_tasks[task_def.name] = celery_task
            logger.info(f"  ✓ {task_def.name}")
            return True

        except Exception as e:
            logger.error(f"  ✗ Failed to register {task_def.name}: {e}")
            return False

    def execute(self, task_name: str, *args, **kwargs) -> Any:
        """Execute task synchronously."""
        celery_task = self._celery_tasks.get(task_name)
        if not celery_task:
            raise ValueError(f"Task {task_name} not registered")

        return celery_task(*args, **kwargs)

    def execute_async(self, task_name: str, *args, **kwargs) -> Any:
        """Execute task asynchronously."""
        celery_task = self._celery_tasks.get(task_name)
        if not celery_task:
            raise ValueError(f"Task {task_name} not registered")

        return celery_task.delay(*args, **kwargs)

    def get_registered_tasks(self) -> list[str]:
        """Get list of registered task names."""
        return list(self._celery_tasks.keys())
