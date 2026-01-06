from .celery_task_adapter import CeleryTaskAdapter

# Alias for backward compatibility
CeleryAdapter = CeleryTaskAdapter

__all__ = ["CeleryTaskAdapter", "CeleryAdapter"]
