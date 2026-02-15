import click
from rich.console import Console
from ..utils import get_containers, load_versions, get_repo_root

console = Console()


@click.command()
def generate_readme() -> None:
    """Update root README.md with container versions."""
    root = get_repo_root()
    readme_path = root / "README.md"

    if not readme_path.exists():
        console.print("[red]Error: README.md not found[/red]")
        return

    with open(readme_path, "r") as f:
        content = f.read()

    start_marker = "<!-- VERSIONS_START -->"
    end_marker = "<!-- VERSIONS_END -->"

    if start_marker not in content or end_marker not in content:
        console.print("[red]Error: Version markers not found in README.md[/red]")
        return

    lines = []
    for c in sorted(get_containers()):
        data = load_versions(c)
        image_name = data.get("image_name", c)
        ghcr_url = f"ghcr.io/expnt/containers/{image_name}"
        lines.append(f"- [{c}](./containers/{c}/README.md) - `{ghcr_url}`")

    new_versions_content = "\n\n" + "\n".join(lines) + "\n\n"
    start_index = content.find(start_marker) + len(start_marker)
    end_index = content.find(end_marker)
    new_content = content[:start_index] + new_versions_content + content[end_index:]

    with open(readme_path, "w") as f:
        f.write(new_content)

    console.print("[green]Successfully updated README.md[/green]")

