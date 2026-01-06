# /c/Users/USER/development/celery_framework/src/tasks/example_tasks.py
"""Example tasks."""


def add(x: int, y: int) -> int:
    """Add two numbers."""
    return x + y


def multiply(x: int, y: int) -> int:
    """Multiply two numbers."""
    return x * y


def process_data(data: dict) -> dict:
    """Process data."""
    return {"processed": True, "input": data}