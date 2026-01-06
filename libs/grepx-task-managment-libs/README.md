# Task Management Library

Framework-agnostic task management library for orchestrators.

## Features

- **Framework Agnostic**: Define tasks once, use in any orchestrator
- **Multiple Sources**: Load from config or database
- **Type Safe**: Full type hints
- **Lightweight**: Minimal dependencies
- **Extensible**: Easy to add custom sources

## Installation

```bash
# Basic
pip install task-management

# With database support
pip install task-management[database]

# All features
pip install task-management[all]
```

## Quick Start

### Basic Usage

```python
from task_management import TaskRegistry, TaskDefinition, TaskManager

# Create registry
registry = TaskRegistry()

# Define task
task_def = TaskDefinition(
    name="tasks.add",
    module_path="my_tasks",
    function_name="add_numbers",
    description="Add two numbers",
    tags=["math"],
    options={"max_retries": 3}
)

# Register
registry.register(task_def)

# Load function
func = task_def.load_function()
result = func(2, 3)
```

### Database Source

```python
from task_management import TaskManager, TaskRegistry
from task_management.sources import DatabaseTaskSource

# Setup
registry = TaskRegistry()
manager = TaskManager(registry)

# Load from database
source = DatabaseTaskSource("sqlite:///tasks.db")
manager.load_from_source(source)

# List tasks
tasks = manager.list_tasks(enabled=True, tags=["celery"])
```

### Add Tasks to Database

```python
from task_management.storage import SQLiteStorage

storage = SQLiteStorage("tasks.db")
storage.add_task(
    name="tasks.process_data",
    module_path="my_tasks",
    function_name="process_data",
    description="Process data batch",
    tags=["celery", "data"],
    options={"time_limit": 300}
)
```

## API Reference

### TaskDefinition

```python
@dataclass
class TaskDefinition:
    name: str                    # Unique task name
    module_path: str            # Python module path
    function_name: str          # Function name in module
    description: str = ""       # Task description
    enabled: bool = True        # Is task enabled
    options: Dict = {}          # Orchestrator-specific options
    tags: List[str] = []        # Tags for filtering
    metadata: Dict = {}         # Additional metadata
```

### TaskRegistry

```python
registry = TaskRegistry()

# Register
registry.register(task_def)

# Get
task = registry.get("task_name")

# Filter
tasks = registry.filter(enabled=True, tags=["celery"])

# List
names = registry.list_names()
```

### TaskManager

```python
manager = TaskManager(registry)

# Load from source
manager.load_from_source(source)

# CRUD operations
manager.create_task(task_def)
task = manager.get_task("name")
manager.update_task("name", enabled=False)
manager.delete_task("name")
```

## License

MIT
