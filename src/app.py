import logging
import sys
from pathlib import Path

from celery import Celery
from omegaconf import DictConfig

# Add src directory to path for task_management imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from task_management import TaskRegistry, TaskManager
from task_management.sources import DatabaseTaskSource, ConfigTaskSource

# Handle both relative and absolute imports
try:
    from .adapters.celery_task_adapter import CeleryTaskAdapter
except ImportError:
    from adapters.celery_task_adapter import CeleryTaskAdapter

logger = logging.getLogger(__name__)


class CeleryAppWrapper:
    """Wrapper for Celery app with task management."""

    def __init__(self, celery_app: Celery, adapter: CeleryTaskAdapter):
        self.app = celery_app
        self.adapter = adapter

    def list_tasks(self) -> list[str]:
        """List registered tasks."""
        return self.adapter.get_registered_tasks()


def create_app(cfg: DictConfig) -> CeleryAppWrapper:
    """
    Create Celery application with task management.

    Args:
        cfg: Hydra configuration

    Returns:
        CeleryAppWrapper instance
    """
    logger.info(f"Creating Celery app: {cfg.app.name}")

    # Create Celery app
    celery_app = Celery(cfg.app.name)

    # Configure Celery
    celery_app.conf.update(
        broker_url=cfg.celery.broker_url,
        result_backend=cfg.celery.result_backend,
        task_serializer=cfg.celery.task_serializer,
        result_serializer=cfg.celery.result_serializer,
        accept_content=list(cfg.celery.accept_content),
        timezone=cfg.celery.timezone,
        enable_utc=cfg.celery.enable_utc,
        worker_prefetch_multiplier=cfg.worker.prefetch_multiplier,
        worker_max_tasks_per_child=cfg.worker.max_tasks_per_child,
        task_track_started=cfg.task.track_started,
        task_time_limit=cfg.task.time_limit,
        task_soft_time_limit=cfg.task.soft_time_limit,
        result_expires=cfg.task.result_expires,
    )

    logger.info("✓ Celery app configured")

    # Setup task management
    registry = TaskRegistry()
    manager = TaskManager(registry)

    # Load tasks based on source
    source_type = cfg.tasks.get("source", "config")

    if source_type == "database":
        logger.info("Loading tasks from database...")
        source = DatabaseTaskSource(
            db_uri=cfg.tasks.database.uri,
            table=cfg.tasks.database.get("table", "tasks"),
        )
        manager.load_from_source(source)

    elif source_type == "config":
        logger.info("Loading tasks from configuration...")
        config_dict = {"tasks": cfg.tasks.get("task_list", [])}
        source = ConfigTaskSource(config_dict)
        manager.load_from_source(source)

    else:
        logger.warning(f"Unknown task source: {source_type}")

    # Register tasks with Celery
    adapter = CeleryTaskAdapter(celery_app, registry)
    adapter.register_all()

    return CeleryAppWrapper(celery_app, adapter)
