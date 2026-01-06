"""Tests for task sources."""

import pytest
from task_management import TaskDefinition
from task_management.sources import ConfigTaskSource, DatabaseTaskSource


class TestConfigTaskSource:
    """Test ConfigTaskSource functionality."""

    def test_load_tasks(self):
        """Test loading tasks from config."""
        config = {
            "tasks": [
                {
                    "name": "test.task",
                    "module_path": "test_module",
                    "function_name": "test_func",
                    "description": "Test task",
                }
            ]
        }
        source = ConfigTaskSource(config)
        tasks = source.load_tasks()
        assert len(tasks) == 1
        assert tasks[0].name == "test.task"

    def test_load_tasks_empty_config(self):
        """Test loading tasks from empty config."""
        config = {}
        source = ConfigTaskSource(config)
        tasks = source.load_tasks()
        assert len(tasks) == 0

    def test_save_task_readonly(self):
        """Test that config source is read-only."""
        config = {"tasks": []}
        source = ConfigTaskSource(config)
        task_def = TaskDefinition(
            name="test.task",
            module_path="test_module",
            function_name="test_func",
        )
        result = source.save_task(task_def)
        assert result is False


class TestDatabaseTaskSource:
    """Test DatabaseTaskSource functionality."""

    def test_init_database(self):
        """Test database initialization."""
        source = DatabaseTaskSource("sqlite:///:memory:")
        assert source._engine is not None
        assert source._table is not None

