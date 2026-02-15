import click
import logging

from .build import build
from .readme import generate_readme
from .upstream import check_upstream, update_version
from .matrix import matrix


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging")
def cli(verbose: bool) -> None:
    """Container management CLI."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="%(name)s: %(message)s",
    )


cli.add_command(build)
cli.add_command(generate_readme)
cli.add_command(check_upstream)
cli.add_command(update_version)
cli.add_command(matrix)
