"""
Task Management Library

Framework-agnostic task management for orchestrators.
"""

from .core.task_definition import TaskDefinition
from .core.task_registry import TaskRegistry
from .core.manager import TaskManager
from .sources.config import ConfigTaskSource
from .sources.database import DatabaseTaskSource

__version__ = "0.1.0"

__all__ = [
    "TaskDefinition",
    "TaskRegistry",
    "TaskManager",
    "ConfigTaskSource",
    "DatabaseTaskSource",
]

