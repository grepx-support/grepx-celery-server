"""Database source example."""
from src.task_management import TaskRegistry, TaskManager
from src.task_management.sources import DatabaseTaskSource
from src.task_management.storage import SQLiteStorage


def setup_database():
    """Setup example database."""
    storage = SQLiteStorage("example_tasks.db")

    # Add example tasks
    storage.add_task(
        name="tasks.add",
        module_path="builtins",
        function_name="sum",
        description="Sum numbers",
        tags=["math"],
        options={"bind": True},
    )

    storage.add_task(
        name="tasks.multiply",
        module_path="operator",
        function_name="mul",
        description="Multiply numbers",
        tags=["math"],
    )

    print("✓ Database setup complete")


def load_tasks():
    """Load tasks from database."""
    registry = TaskRegistry()
    manager = TaskManager(registry)

    # Load from database
    source = DatabaseTaskSource("sqlite:///example_tasks.db")
    count = manager.load_from_source(source)
    print(f"✓ Loaded {count} tasks")

    # List tasks
    for task_def in manager.list_tasks():
        print(f"  - {task_def.name}: {task_def.description}")


if __name__ == "__main__":
    setup_database()
    load_tasks()

