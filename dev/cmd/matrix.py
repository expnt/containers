import click
import os
import json
import requests
from ..utils import get_containers, load_versions, compute_tag


def get_changed_containers(files: list[str]) -> list[str]:
    """Filter containers from changed files list."""
    changed = set()
    for f in files:
        if f.startswith("containers/"):
            parts = f.split("/")
            if len(parts) > 1:
                changed.add(parts[1])
        elif f.startswith("dev/"):
            return get_containers()
    return list(changed) if changed else []


def image_exists(image: str, tag: str) -> bool:
    """Check if image:tag exists in GHCR."""
    token = os.environ.get("GITHUB_TOKEN", "")
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "")
    url = f"https://ghcr.io/v2/{owner}/containers/{image}/manifests/{tag}"
    resp = requests.head(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.oci.image.index.v1+json",
        },
    )
    return resp.status_code == 200


@click.command()
@click.option("--changed-files", help="Comma-separated list of changed files")
@click.option(
    "--skip-existing", is_flag=True, help="Skip images that already exist in registry"
)
def matrix(changed_files: str | None, skip_existing: bool) -> None:
    """Output build matrix JSON for CI."""
    if changed_files:
        containers = get_changed_containers(changed_files.split(","))
    else:
        containers = get_containers()
    include = []
    for c in containers:
        data = load_versions(c)
        image_name = data.get("image_name", c)
        tag_pattern = data.get("tag_pattern", "{base_version}")
        for v_entry in data.get("versions", []):
            tag = compute_tag(tag_pattern, v_entry)
            if skip_existing and image_exists(image_name, tag):
                continue
            include.append(
                {
                    "container": c,
                    "version": v_entry.get("base_version"),
                    "tag": tag,
                }
            )
    print(json.dumps({"include": include}))
