import logging
import re
import requests
from typing import List
from datetime import datetime, timedelta, timezone
from github import Github, GithubException

log = logging.getLogger(__name__)


def get_recent_releases(repo: str, pattern: str, hours: int = 24) -> List[str]:
    """Fetches release tags published in the last N hours matching a pattern."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    prog = re.compile(pattern)
    g = Github()

    log.debug(f"Fetching releases from {repo}")
    try:
        releases = g.get_repo(repo).get_releases()
        result = [
            r.tag_name.lstrip("v")
            for r in releases
            if r.published_at and r.published_at > since and prog.match(r.tag_name)
        ]
        log.debug(f"Found {len(result)} matching releases for {repo}")
        return result
    except GithubException as e:
        log.warning(f"Failed to fetch releases from {repo}: {e}")
        return []


def get_recent_package_tags(
    package_path: str, pattern: str, hours: int = 24
) -> List[str]:
    """Fetches GHCR package tags published in the last N hours matching a pattern."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    prog = re.compile(pattern)

    parts = package_path.removeprefix("ghcr.io/").split("/")
    owner, package = parts[0], "/".join(parts[1:])

    for entity_type in ["orgs", "users"]:
        url = f"https://api.github.com/{entity_type}/{owner}/packages/container/{package.replace('/', '%2F')}/versions"
        log.debug(f"Fetching GHCR tags from {url}")
        try:
            res = requests.get(url)
            res.raise_for_status()
            tags_with_dates = [
                (tag, datetime.fromisoformat(v["created_at"].replace("Z", "+00:00")))
                for v in res.json()
                for tag in v["metadata"]["container"]["tags"]
                if prog.match(tag)
            ]
            result = [
                tag
                for tag, dt in sorted(tags_with_dates, key=lambda x: x[1], reverse=True)
                if dt > since
            ]
            log.debug(f"Found {len(result)} matching tags for {package_path}")
            return result
        except requests.RequestException as e:
            log.debug(f"Failed {entity_type} lookup for {package_path}: {e}")
            continue
    log.warning(f"No tags found for {package_path}")
    return []
