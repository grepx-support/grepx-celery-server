"""Tests for TaskRegistry."""

import pytest
from task_management import TaskRegistry, TaskDefinition


class TestTaskRegistry:
    """Test TaskRegistry functionality."""

    def test_register_task(self):
        """Test registering a task."""
        registry = TaskRegistry()
        task_def = TaskDefinition(
            name="test.task",
            module_path="test_module",
            function_name="test_func",
        )
        registry.register(task_def)
        assert "test.task" in registry
        assert len(registry) == 1

    def test_get_task(self):
        """Test getting a task."""
        registry = TaskRegistry()
        task_def = TaskDefinition(
            name="test.task",
            module_path="test_module",
            function_name="test_func",
        )
        registry.register(task_def)
        retrieved = registry.get("test.task")
        assert retrieved is not None
        assert retrieved.name == "test.task"

    def test_filter_by_enabled(self):
        """Test filtering by enabled status."""
        registry = TaskRegistry()
        task1 = TaskDefinition(
            name="task1", module_path="mod", function_name="func1", enabled=True
        )
        task2 = TaskDefinition(
            name="task2", module_path="mod", function_name="func2", enabled=False
        )
        registry.register(task1)
        registry.register(task2)
        enabled_tasks = registry.filter(enabled=True)
        assert len(enabled_tasks) == 1
        assert enabled_tasks[0].name == "task1"

    def test_filter_by_tags(self):
        """Test filtering by tags."""
        registry = TaskRegistry()
        task1 = TaskDefinition(
            name="task1", module_path="mod", function_name="func1", tags=["celery"]
        )
        task2 = TaskDefinition(
            name="task2", module_path="mod", function_name="func2", tags=["dagster"]
        )
        registry.register(task1)
        registry.register(task2)
        celery_tasks = registry.filter(tags=["celery"])
        assert len(celery_tasks) == 1
        assert celery_tasks[0].name == "task1"

    def test_unregister_task(self):
        """Test unregistering a task."""
        registry = TaskRegistry()
        task_def = TaskDefinition(
            name="test.task",
            module_path="test_module",
            function_name="test_func",
        )
        registry.register(task_def)
        assert len(registry) == 1
        registry.unregister("test.task")
        assert len(registry) == 0

