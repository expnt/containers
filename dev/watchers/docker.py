import logging
import re
import requests
from typing import List
from datetime import datetime, timedelta, timezone

log = logging.getLogger(__name__)


def get_recent_tags(image: str, pattern: str, hours: int = 24) -> List[str]:
    """Fetches tags published in the last N hours matching a pattern from Docker Hub."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    prog = re.compile(pattern)

    image = image.removeprefix("docker.io/")
    if "/" not in image:
        image = f"library/{image}"

    url = f"https://registry.hub.docker.com/v2/repositories/{image}/tags"
    log.debug(f"Fetching tags from {url}")
    res = requests.get(url, params={"page_size": 100, "ordering": "-last_updated"})
    res.raise_for_status()

    tags_with_dates = [
        (t["name"], datetime.fromisoformat(t["last_updated"].replace("Z", "+00:00")))
        for t in res.json().get("results", [])
        if prog.match(t["name"])
    ]
    result = [
        name
        for name, dt in sorted(tags_with_dates, key=lambda x: x[1], reverse=True)
        if dt > since
    ]
    log.debug(f"Found {len(result)} matching tags for {image}")
    return result
