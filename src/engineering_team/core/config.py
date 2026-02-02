"""Configuration file handling for engineering-team."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .schema import ProjectConfig


CONFIG_FILE_NAME = "engineering-team.json"


def get_config_path(project_dir: Optional[Path] = None) -> Path:
    """Get the path to the configuration file."""
    if project_dir is None:
        project_dir = Path.cwd()
    return project_dir / CONFIG_FILE_NAME


def config_exists(project_dir: Optional[Path] = None) -> bool:
    """Check if a configuration file exists."""
    return get_config_path(project_dir).exists()


def load_config(project_dir: Optional[Path] = None) -> Optional[ProjectConfig]:
    """Load configuration from the project directory."""
    config_path = get_config_path(project_dir)
    if not config_path.exists():
        return None

    with open(config_path, "r") as f:
        data = json.load(f)

    # Handle datetime conversion
    if "installed_at" in data:
        if isinstance(data["installed_at"], str):
            data["installed_at"] = datetime.fromisoformat(
                data["installed_at"].replace("Z", "+00:00")
            )

    # Handle snake_case vs camelCase
    if "installedAt" in data:
        data["installed_at"] = datetime.fromisoformat(
            data["installedAt"].replace("Z", "+00:00")
        )
        del data["installedAt"]

    if "cliVersion" in data:
        data["cli_version"] = data["cliVersion"]
        del data["cliVersion"]

    return ProjectConfig(**data)


def save_config(config: ProjectConfig, project_dir: Optional[Path] = None) -> Path:
    """Save configuration to the project directory."""
    config_path = get_config_path(project_dir)

    # Convert to JSON-serializable dict with camelCase keys
    data = {
        "version": config.version,
        "agents": config.agents,
        "skills": config.skills,
        "installedAt": config.installed_at.isoformat(),
        "cliVersion": config.cli_version,
    }

    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)

    return config_path
