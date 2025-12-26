import click
import subprocess
import os
import sys
from typing import Optional
from rich.console import Console
from ..common import get_containers, load_versions, compute_tag

console = Console()


@click.command()
@click.argument("container", required=False)
@click.option("--all", "all_containers", is_flag=True, help="Build all containers")
@click.option("--output", "-o", is_flag=True, help="Output image to Docker")
@click.option("--push", "-p", is_flag=True, help="Push image to registry")
@click.option(
    "--multiplatform", "-m", is_flag=True, help="Build for multiple platforms"
)
@click.option("--version", "target_version", help="Build specific version only")
@click.option("--repo-owner", help="Set repository owner")
def build(
    container: Optional[str],
    all_containers: bool,
    output: bool,
    push: bool,
    multiplatform: bool,
    target_version: Optional[str],
    repo_owner: Optional[str],
) -> None:
    """Build container images using Earthly."""
    if not container and not all_containers:
        console.print("[red]Error: Specify a container or use --all[/red]")
        sys.exit(1)

    containers = [container] if container else get_containers()
    repo_owner = repo_owner or os.environ.get("GITHUB_REPOSITORY_OWNER", os.getlogin())

    for c in containers:
        try:
            data = load_versions(c)
            image_name = data.get("image_name", c)
            tag_pattern = data.get("tag_pattern", "{base_version}")

            versions = data.get("versions", [])
            if target_version:
                versions = [
                    v for v in versions if v.get("base_version") == target_version
                ]
                if not versions:
                    console.print(
                        f"[yellow]Version {target_version} not found for {c}, skipping[/yellow]"
                    )
                    continue

            for v_entry in versions:
                tag = compute_tag(tag_pattern, v_entry)
                console.print(f"[bold blue]Building {image_name}:{tag}...[/bold blue]")

                build_args = [
                    "--build-arg",
                    f"GITHUB_REPOSITORY_OWNER={repo_owner}",
                    "--build-arg",
                    f"TAG={tag}",
                ]

                for k, v in v_entry.items():
                    build_args.extend(["--build-arg", f"{k.upper()}={v}"])

                target = "+build-multiplatform" if (multiplatform or push) else "+build"

                cmd = ["earthly"]
                if push:
                    cmd.append("--push")
                if output and not push:
                    cmd.append("--output")

                cmd.extend(build_args)
                cmd.append(f"./containers/{c}{target}")

                console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
                subprocess.run(cmd, check=True)
                console.print(
                    f"[bold green]Successfully built {image_name}:{tag}[/bold green]"
                )

        except Exception as e:
            console.print(f"[red]Error building {c}: {e}[/red]")
            if not all_containers:
                sys.exit(1)
