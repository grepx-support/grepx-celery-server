"""Basic usage example."""
from src.task_management import TaskRegistry, TaskDefinition


def example_task(x: int, y: int) -> int:
    """Example task function."""
    return x + y


def main():
    # Create registry
    registry = TaskRegistry()

    # Define task
    task_def = TaskDefinition(
        name="example.add",
        module_path="__main__",
        function_name="example_task",
        description="Add two numbers",
        tags=["example", "math"],
        options={"max_retries": 3},
    )

    # Register
    registry.register(task_def)

    # Use task
    func = task_def.load_function()
    result = func(2, 3)
    print(f"Result: {result}")

    # List tasks
    print(f"Registered tasks: {registry.list_names()}")


if __name__ == "__main__":
    main()

