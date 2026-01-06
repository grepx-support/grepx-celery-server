import os

from omegaconf import OmegaConf, DictConfig
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads all configuration files."""

    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        if not self.config_dir.exists() or not self.config_dir.is_dir():
            raise ValueError(f"Config directory does not exist: {self.config_dir}")

    def load_all(self) -> DictConfig:
        """Load all configuration files, including enabled connections."""
        app_file = self.config_dir / "config.yaml"
        if not app_file.exists():
            raise FileNotFoundError(f"Missing config file: {app_file}")

        app_config = OmegaConf.load(app_file)

        connections = getattr(app_config, "connections", [])
        for idx, conn in enumerate(connections):
            enabled = conn.get("enabled", True)
            if not enabled:
                continue

            config_file = conn.get("config_file")
            if not config_file:
                logger.warning(f"Connection at index {idx} has no config_file, skipping")
                continue

            conn_path = self.config_dir / config_file
            if not conn_path.exists():
                logger.warning(f"Connection config {conn_path} does not exist, skipping")
                continue

            conn_config = OmegaConf.load(conn_path)
            app_config = OmegaConf.merge(app_config, conn_config)
            logger.info(f"Merged connection config: {conn_path}")

        return app_config


def _load_config():
    """Load configuration from YAML file."""
    # Get the project root directory (parent of src)
    project_root = Path(__file__).parent.parent
    config_dir = project_root / "config"

    if not config_dir.exists():
        raise FileNotFoundError(f"Configuration directory not found: {config_dir}")

    # Use ConfigLoader to load all configs
    config_loader = ConfigLoader(config_dir)
    cfg = config_loader.load_all()

    # Override with environment variables if present
    if "APP_ENV" in os.environ:
        cfg.app.environment = os.environ["APP_ENV"]
    if "CELERY_BROKER_URL" in os.environ:
        cfg.celery.broker_url = os.environ["CELERY_BROKER_URL"]
    if "CELERY_RESULT_BACKEND" in os.environ:
        cfg.celery.result_backend = os.environ["CELERY_RESULT_BACKEND"]

    return cfg
