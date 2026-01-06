# /c/Users/USER/development/celery_framework/src/main.py
"""
Celery application launcher.

Run:
    python src/main.py
    or
    ./run.sh start
"""

import logging
import signal
import sys
import threading
from pathlib import Path

from celery import Celery

# Add src directory to path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

logger = logging.getLogger(__name__)


def create_celery_app() -> Celery:
    from app import create_app
    from config_loader import _load_config

    cfg = _load_config()
    wrapper = create_app(cfg)

    logger.info("Celery app initialized")
    logger.info(f"Registered tasks: {wrapper.list_tasks()}")

    return wrapper.app


# Create module-level app instance for CLI compatibility
app = create_celery_app()


def start_worker(celery_app: Celery) -> None:
    argv = [
        "worker",
        "--loglevel=info",
        "--pool=solo",  # Windows compatibility
    ]
    celery_app.worker_main(argv)


def start_beat(celery_app: Celery) -> None:
    argv = [
        "beat",
        "--loglevel=info",
    ]
    celery_app.start(argv)


def start_flower() -> None:
    import subprocess

    subprocess.run([
        sys.executable, "-m", "flower",
        "--port=5555",
        "--address=0.0.0.0",
        f"--broker={app.conf.broker_url}"
    ])


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    shutdown_event = threading.Event()

    def handle_shutdown(signum, frame):
        logger.info("Shutting down...")
        shutdown_event.set()

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    threading.Thread(target=start_worker, args=(app,), daemon=True).start()
    threading.Thread(target=start_beat, args=(app,), daemon=True).start()
    threading.Thread(target=start_flower, daemon=True).start()

    logger.info("Celery services started")
    logger.info("Flower UI: http://localhost:5555")
    shutdown_event.wait()


if __name__ == "__main__":
    main()
