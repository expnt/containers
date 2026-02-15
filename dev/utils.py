import os
import subprocess
import yaml
from pathlib import Path
from typing import Dict, Any, List


def get_repo_root() -> Path:
    """Returns the root directory of the repository."""
    return Path(__file__).parent.parent


def load_versions(container_name: str) -> Dict[str, Any]:
    """Loads the versions.yaml file for a given container."""
    path = get_repo_root() / "containers" / container_name / "versions.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Versions file not found for {container_name}")
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        return data


def get_containers() -> List[str]:
    """Returns a list of all container names in the containers/ directory."""
    containers_dir = get_repo_root() / "containers"
    return [
        d.name
        for d in containers_dir.iterdir()
        if d.is_dir() and (d / "versions.yaml").exists()
    ]


def compute_tag(tag_pattern: str, version_vars: Dict[str, Any]) -> str:
    """Computes the final image tag based on a pattern and version variables."""
    return tag_pattern.format(**version_vars)


def get_default_repo_owner() -> str:
    """Get repo owner from GITHUB_REPOSITORY (owner/repo) or git remote."""
    if repo := os.environ.get("GITHUB_REPOSITORY"):
        return repo.split("/")[0]
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            if "github.com" in url:
                return url.split("github.com")[1].strip("/:").split("/")[0]
    except Exception:
        pass
    return "local"
