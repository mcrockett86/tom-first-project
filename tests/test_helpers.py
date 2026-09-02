"""Test utilities."""

import json
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    with open(config_path) as f:
        return json.load(f)


def save_config(path: Path, data: Dict[str, Any]) -> None:
    """Save configuration to JSON file atomically."""
    temp_path = path.with_suffix('.tmp')
    with open(temp_path, 'w') as f:
        json.dump(data, f, indent=2)
    temp_path.rename(path)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent
