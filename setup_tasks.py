# /c/Users/USER/development/celery_framework/setup_tasks.py
"""Setup example tasks in database."""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from task_management.storage import SQLiteStorage


def setup():
    """Setup example tasks."""
    storage = SQLiteStorage("tasks.db")

    # Add example tasks
    storage.add_task(
        name="tasks.add",
        module_path="tasks.example_tasks",
        function_name="add",
        description="Add two numbers",
        tags=["math", "celery"],
        options={"bind": True, "max_retries": 3},
    )

    storage.add_task(
        name="tasks.multiply",
        module_path="tasks.example_tasks",
        function_name="multiply",
        description="Multiply two numbers",
        tags=["math", "celery"],
    )

    storage.add_task(
        name="tasks.process_data",
        module_path="tasks.example_tasks",
        function_name="process_data",
        description="Process data batch",
        tags=["data", "celery"],
        options={"time_limit": 300},
    )

    print("Example tasks added to database")

    # List tasks
    tasks = storage.list_tasks()
    print(f"\nTotal tasks: {len(tasks)}")
    for task in tasks:
        print(f"  - {task['name']}: {task['description']}")


if __name__ == "__main__":
    setup()
