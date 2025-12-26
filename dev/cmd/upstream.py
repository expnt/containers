import click
import json
import yaml
from typing import Optional
from rich.console import Console
from ..utils import get_containers, load_versions, get_repo_root
from ..watchers import docker, github

console = Console()


@click.command()
@click.argument("container", required=False)
@click.option("--hours", default=24, help="Check updates in the last N hours")
@click.option("--json-output", "-j", is_flag=True, help="Output JSON for CI")
def check_upstream(container: Optional[str], hours: int, json_output: bool) -> None:
    """Check for upstream updates."""
    containers = [container] if container else get_containers()
    results = []

    for c in containers:
        data = load_versions(c)
        container_updates = []
        for watch in data.get("watch", []):
            current_val = str(data["versions"][0].get(watch["target"]))
            discovered = []
            if watch["type"] == "docker":
                if watch["source"].startswith("ghcr.io/"):
                    discovered = github.get_recent_package_tags(
                        watch["source"], watch["pattern"], hours=hours
                    )
                else:
                    discovered = docker.get_recent_tags(
                        watch["source"], watch["pattern"], hours=hours
                    )
            elif watch["type"] == "github":
                discovered = github.get_recent_releases(
                    watch["source"], watch["pattern"], hours=hours
                )

            new_versions = [v for v in discovered if v != current_val]
            if new_versions:
                container_updates.append(
                    {"target": watch["target"], "version": new_versions[0]}
                )
                if not json_output:
                    console.print(
                        f"[yellow]Updates available for {c} ({watch['target']}): {current_val} -> {', '.join(new_versions)}[/yellow]"
                    )
            elif not json_output:
                if discovered:
                    console.print(
                        f"[green]{c} ({watch['target']}) is up to date (current: {current_val})[/green]"
                    )
                else:
                    console.print(
                        f"[green]{c} ({watch['target']}) no recent updates in last {hours}h[/green]"
                    )

        if container_updates:
            results.append({"container": c, "updates": container_updates})

    if json_output:
        print(json.dumps(results[0] if container and results else results))


@click.command()
@click.argument("container")
@click.option("--target", required=True, help="Target field to update")
@click.option("--version", "new_version", required=True, help="New version value")
def update_version(container: str, target: str, new_version: str) -> None:
    """Update a version field in a container's versions.yaml."""
    root = get_repo_root()
    version_file = root / "containers" / container / "versions.yaml"

    with open(version_file) as f:
        data = yaml.safe_load(f)

    if target == "base_version":
        data["versions"].insert(0, {"base_version": new_version})
    else:
        data["versions"][0][target] = new_version

    with open(version_file, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    console.print(f"[green]Updated {container} {target} to {new_version}[/green]")

