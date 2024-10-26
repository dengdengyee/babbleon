import click
import json
import toml
from pathlib import Path
from importlib_resources import files

from .config import BabbleonConfig
from .translate import BabbleonTranslator

config_file = Path("babbleon.json")


@click.group()
@click.pass_context
def cli(ctx):
    # if command is not init, check if config file exists
    if ctx.invoked_subcommand != "init":
        if not config_file.exists():
            raise click.UsageError(
                "babbleon.json not found. Please run `babbleon init` first."
            )
        ctx.obj = BabbleonConfig(config_file)


@cli.command()
def init():
    """Initialize a new project"""

    # Check if file already exists
    if config_file.exists():
        if not click.confirm(
            "babbleon.json already exists. Do you want to overwrite it?"
        ):
            click.echo("Aborted.")
            return

    # Read template using importlib.resources
    template_path = files("babbleon.templates").joinpath("babbleon.json")
    with open(template_path, "r", encoding="utf-8") as src:
        config_content = src.read()

    with open(config_file, "w", encoding="utf-8") as dest:
        dest.write(config_content)

    click.echo("Created babbleon.json with sample configuration")

    config = BabbleonConfig(config_file)

    reference_file = Path(config.get_reference_file())
    reference_path = files("babbleon.templates").joinpath("reference.toml")
    with open(reference_path, "r", encoding="utf-8") as src:
        reference_content = src.read()

    if not reference_file.exists():
        reference_file.parent.mkdir(parents=True, exist_ok=True)
    with open(reference_file, "w", encoding="utf-8") as dest:
        dest.write(reference_content)

    click.echo("Created reference-template.toml with sample text")


@cli.command()
@click.pass_context
def generate(ctx):
    """Generate the translation files for the target languages"""
    config = ctx.obj
    reference_file_content = config.get_reference_file().read_text(encoding="utf-8")
    translator = BabbleonTranslator(reference_file_content, config.get_output_format())
    output_dir = config.get_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    for language in config.get_target_languages():
        print(f"Translating to {language}")
        local_json_string = translator.translate(language)
        local_json_file = output_dir.joinpath(f"{language}.json")
        with open(local_json_file, "w", encoding="utf-8") as dest:
            dest.write(local_json_string)


if __name__ == "__main__":
    cli()
