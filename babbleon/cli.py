import click
import json
from pathlib import Path
from importlib import resources

from .config import BabbleonConfig

config_file = Path("babbleon.json")


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = BabbleonConfig(config_file)


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize a new project"""

    # Check if file already exists
    if config_file.exists():
        if not click.confirm(
            "babbleon.json already exists. Do you want to overwrite it?"
        ):
            click.echo("Aborted.")
            return

    # Read template using importlib.resources
    with resources.open_text("babbleon", "config-template.json") as src:
        config_content = src.read()

    with open(config_file, "w", encoding="utf-8") as dest:
        dest.write(config_content)

    click.echo("Created babbleon.json with sample configuration")

    reference_file = Path(ctx.obj.get_reference_file())
    with resources.open_text("babbleon", "reference-template.toml") as src:
        reference_content = src.read()

    if not reference_file.exists():
        reference_file.parent.mkdir(parents=True, exist_ok=True)
    with open(reference_file, "w", encoding="utf-8") as dest:
        dest.write(reference_content)

    click.echo("Created reference-template.toml with sample text")


if __name__ == "__main__":
    cli()
