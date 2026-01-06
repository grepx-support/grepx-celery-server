# src/celery_framework/__init__.py
"""Generic Celery framework for distributed task execution."""

__all__ = [
    "CeleryConfig",
    "WorkerConfig",
    "TaskConfig",
    "TaskRegistry",
    "task",
]

from src.config import CeleryConfig, WorkerConfig, TaskConfig
from src.tasks.decorators import task
from src.tasks.task_registry import TaskRegistry
