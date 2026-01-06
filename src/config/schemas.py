"""Configuration schemas using Hydra dataclasses."""
from dataclasses import dataclass, field
from typing import List
from hydra.core.config_store import ConfigStore


@dataclass
class AppConfig:
    """Application metadata configuration."""
    name: str = "celery_framework"
    version: str = "1.0.0"
    environment: str = "local"


@dataclass
class CeleryConfig:
    """Celery broker and serialization configuration."""
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/1"
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: List[str] = field(default_factory=lambda: ["json"])
    timezone: str = "Asia/Kolkata"
    enable_utc: bool = True


@dataclass
class WorkerConfig:
    """Worker process configuration."""
    prefetch_multiplier: int = 1
    max_tasks_per_child: int = 50


@dataclass
class TaskConfig:
    """Task execution configuration."""
    track_started: bool = True
    time_limit: int = 1800
    soft_time_limit: int = 1500
    result_expires: int = 3600


@dataclass
class TaskDirectoryConfig:
    """Task directory loading configuration."""
    path: str
    pattern: str = "tasks.py"


@dataclass
class TasksConfig:
    """Tasks loading configuration."""
    modules: List[str] = field(default_factory=list)
    directories: List[TaskDirectoryConfig] = field(default_factory=list)


@dataclass
class Config:
    """Root configuration."""
    app: AppConfig = field(default_factory=AppConfig)
    celery: CeleryConfig = field(default_factory=CeleryConfig)
    worker: WorkerConfig = field(default_factory=WorkerConfig)
    task: TaskConfig = field(default_factory=TaskConfig)
    tasks: TasksConfig = field(default_factory=TasksConfig)


# Register with Hydra
def register_configs():
    """Register all config schemas with Hydra."""
    cs = ConfigStore.instance()
    cs.store(name="config", node=Config)


register_configs()