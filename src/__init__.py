"""Celery Framework - A flexible Celery task management framework."""
from .app import CeleryAppWrapper, create_app

__version__ = "1.0.0"
__all__ = [
    "CeleryAppWrapper",
    "create_app",
]