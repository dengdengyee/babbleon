import click
from pathlib import Path
from typing import List
from .config import babbleonConfig
from .validator import ReferenceValidator, format_validation_result
import json
from .translator import Translator

@click.group()
@click.pass_context
def cli(ctx):
    """babbleon - Translation Management Tool"""
    ctx.obj = babbleonConfig()

# ... (init, check, and config commands remain the same) ...

@cli.group()
def validate():
    """Validate references and documentation"""
    pass

@validate.command(name='ref')
@click.pass_obj
@click.argument('reference_path', required=True)
def validate_reference(config: babbleonConfig, reference_path: str):
    """
    Validate a specific reference path
    
    Example: babbleon validate ref tabs.index.button
    """
    try:
        reference_data = config.read_reference()
        validator = ReferenceValidator(reference_data, "")  # Empty docs content for single ref
        
        result = validator.validate_reference(reference_path)
        click.echo(format_validation_result(result))
            
    except click.ClickException as e:
        raise e

@validate.command(name='docs')
@click.pass_obj
def validate_docs(config: babbleonConfig):
    """
    Validate all references in docs.md against reference.yaml
    
    Example: babbleon validate docs
    """
    try:
        reference_data = config.read_reference()
        docs_content = config.read_docs()
        validator = ReferenceValidator(reference_data, docs_content)
        
        results = validator.validate_docs()
        
        click.echo("📚 Validating references in docs.md...")
        
        if results['valid']:
            click.echo("\n✅ Valid references:")
            for result in results['valid']:
                click.echo(f"  • {format_validation_result(result)}")
        
        if results['invalid']:
            click.echo("\n❌ Invalid references:")
            for result in results['invalid']:
                click.echo(f"  • {format_validation_result(result)}")
            raise click.ClickException(
                f"\nFound {len(results['invalid'])} invalid references in docs.md"
            )
        else:
            click.echo("\n✨ All references are valid!")
            
    except click.ClickException as e:
        raise e
    

@cli.group()
def translate():
    """Translation related commands"""
    pass

@translate.command(name='generate')
@click.pass_obj
@click.argument('lang_code')
@click.option('--output', '-o', help='Output file path')
def generate_translation(config: babbleonConfig, lang_code: str, output: str):
    """
    Generate translation for specified language
    
    Example: babbleon translate generate ko -o ko.json
    """
    try:
        # Validate language code is configured
        if lang_code not in config.languages:
            raise click.ClickException(
                f"Language '{lang_code}' not configured. "
                "Add it first with: babbleon config --add-language {lang_code}"
            )
        
        # Create translator
        reference_data = config.read_reference()
        docs_content = config.read_docs()
        translator = Translator(reference_data, docs_content)
        
        click.echo(f"🌍 Generating translation for {lang_code}...")
        
        # Generate translation
        translated_content = translator.translate(lang_code)
        
        # Validate translation structure
        translator.validate_translation(translated_content)
        
        # Save or print result
        if output:
            output_path = Path(output)
            output_path.write_text(
                json.dumps(translated_content, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            click.echo(f"✨ Translation saved to: {output_path}")
        else:
            click.echo("\n📝 Generated translation:")
            click.echo(json.dumps(translated_content, ensure_ascii=False, indent=2))
        
    except click.ClickException as e:
        raise e
    

@translate.command(name='all')
@click.pass_obj
@click.option(
    '--output', '-o',
    required=True,
    help='Output directory for translation files',
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path)
)
def translate_all(config: babbleonConfig, output: Path):
    """
    Generate translations for all configured languages
    
    Example: babbleon translate all -o ./translations
    """
    try:
        # Create output directory if it doesn't exist
        output.mkdir(parents=True, exist_ok=True)
        
        # Validate languages are configured
        if not config.languages:
            raise click.ClickException(
                "No languages configured. "
                "Add languages first with: babbleon config --add-language <lang_code>"
            )
        
        # Create translator
        reference_data = config.read_reference()
        docs_content = config.read_docs()
        translator = Translator(reference_data, docs_content)
        
        # Show progress
        click.echo(f"🌍 Generating translations for: {', '.join(config.languages)}")
        click.echo(f"📁 Output directory: {output}")
        
        successes = []
        failures = []
        
        # Process each language
        with click.progressbar(config.languages, label='Translating') as languages:
            for lang_code in languages:
                try:
                    # Translate content
                    translated_content = translator.translate(lang_code)
                    translator.validate_translation(translated_content)
                    
                    # Save to file
                    output_file = output / f"{lang_code}.json"
                    output_file.write_text(
                        json.dumps(translated_content, ensure_ascii=False, indent=2),
                        encoding='utf-8'
                    )
                    
                    successes.append(lang_code)
                    
                except Exception as e:
                    failures.append((lang_code, str(e)))
        
        # Report results
        if successes:
            click.echo("\n✅ Successfully translated:")
            for lang in successes:
                click.echo(f"  • {lang} -> {output / f'{lang}.json'}")
        
        if failures:
            click.echo("\n❌ Failed translations:")
            for lang, error in failures:
                click.echo(f"  • {lang}: {error}")
            
            if not successes:
                raise click.ClickException("All translations failed")
        
        click.echo(f"\n✨ Completed! Translations saved in: {output}")
        
    except click.ClickException as e:
        raise e
    except Exception as e:
        raise click.ClickException(f"Translation failed: {str(e)}")