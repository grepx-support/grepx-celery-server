"""Tests for TaskManager."""

import pytest
from task_management import TaskRegistry, TaskManager, TaskDefinition


class TestTaskManager:
    """Test TaskManager functionality."""

    def test_create_task(self):
        """Test creating a task."""
        registry = TaskRegistry()
        manager = TaskManager(registry)
        task_def = TaskDefinition(
            name="test.task",
            module_path="test_module",
            function_name="test_func",
        )
        manager.create_task(task_def)
        assert manager.count() == 1

    def test_get_task(self):
        """Test getting a task."""
        registry = TaskRegistry()
        manager = TaskManager(registry)
        task_def = TaskDefinition(
            name="test.task",
            module_path="test_module",
            function_name="test_func",
        )
        manager.create_task(task_def)
        retrieved = manager.get_task("test.task")
        assert retrieved is not None
        assert retrieved.name == "test.task"

    def test_list_tasks(self):
        """Test listing tasks."""
        registry = TaskRegistry()
        manager = TaskManager(registry)
        task1 = TaskDefinition(
            name="task1", module_path="mod", function_name="func1", enabled=True
        )
        task2 = TaskDefinition(
            name="task2", module_path="mod", function_name="func2", enabled=False
        )
        manager.create_task(task1)
        manager.create_task(task2)
        all_tasks = manager.list_tasks()
        assert len(all_tasks) == 2
        enabled_tasks = manager.list_tasks(enabled=True)
        assert len(enabled_tasks) == 1

    def test_update_task(self):
        """Test updating a task."""
        registry = TaskRegistry()
        manager = TaskManager(registry)
        task_def = TaskDefinition(
            name="test.task",
            module_path="test_module",
            function_name="test_func",
            enabled=True,
        )
        manager.create_task(task_def)
        manager.update_task("test.task", enabled=False)
        updated = manager.get_task("test.task")
        assert updated.enabled is False

    def test_delete_task(self):
        """Test deleting a task."""
        registry = TaskRegistry()
        manager = TaskManager(registry)
        task_def = TaskDefinition(
            name="test.task",
            module_path="test_module",
            function_name="test_func",
        )
        manager.create_task(task_def)
        assert manager.count() == 1
        manager.delete_task("test.task")
        assert manager.count() == 0

    def test_count(self):
        """Test counting tasks."""
        registry = TaskRegistry()
        manager = TaskManager(registry)
        assert manager.count() == 0
        manager.create_task(
            TaskDefinition(
                name="task1", module_path="mod", function_name="func1"
            )
        )
        assert manager.count() == 1

