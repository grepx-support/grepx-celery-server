"""Task definition - framework agnostic."""

from dataclasses import dataclass, field
from typing import Dict, Any, Callable, Optional
from datetime import datetime


@dataclass
class TaskDefinition:
    """Framework-agnostic task definition."""

    name: str
    module_path: str
    function_name: str
    description: str = ""
    enabled: bool = True
    options: Dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Set timestamps."""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()

    @property
    def full_path(self) -> str:
        """Get full import path."""
        return f"{self.module_path}.{self.function_name}"

    def load_function(self) -> Callable:
        """Dynamically load the function."""
        import importlib

        module = importlib.import_module(self.module_path)
        return getattr(module, self.function_name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "module_path": self.module_path,
            "function_name": self.function_name,
            "description": self.description,
            "enabled": self.enabled,
            "options": self.options,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskDefinition":
        """Create from dictionary."""
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)

