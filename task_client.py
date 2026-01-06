# task_client.py - Simple task client

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import app


class TaskClient:
    """Simple client to interact with Celery tasks."""

    def __init__(self):
        self.app = app

    def list(self):
        """List all registered tasks."""
        tasks = [name for name in self.app.tasks.keys()
                 if not name.startswith('celery_framework.')]

        print("\nRegistered Tasks:")
        print("-" * 40)
        for name in sorted(tasks):
            print(f"  • {name}")
        print()

        return tasks

    def submit(self, task_name: str, *args, **kwargs):
        """Submit a task and return result."""
        if task_name not in self.app.tasks:
            raise ValueError(f"Task '{task_name}' not found")

        result = self.app.send_task(task_name, args=args, kwargs=kwargs)
        print(f"Task submitted: {result.id}")
        return result

    def get_result(self, task_id: str, timeout: int = 10):
        """Get task result by ID."""
        from celery.result import AsyncResult

        result = AsyncResult(task_id, app=self.app)
        return result.get(timeout=timeout)

    def execute(self, task_name: str, *args, **kwargs):
        """Submit task and wait for result."""
        result = self.submit(task_name, *args, **kwargs)

        try:
            output = result.get(timeout=10)
            print(f"Result: {output}")
            return output
        except Exception as e:
            print(f"Error: {e}")
            return None


# Usage
if __name__ == "__main__":
    client = TaskClient()

    # List tasks
    client.list()

    # Execute task
    result = client.execute("tasks.add", 10, 5)
    print(f"Add Task Result: {result}")
