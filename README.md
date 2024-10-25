# babbleon

Manage your app translations with ease. babbleon is a command-line tool that helps you manage, validate, and generate translations for your applications.

## Features

- 🚀 **Quick Setup**: Initialize translation configs with a single command
- ✅ **Validation**: Ensure translation references are valid and documented
- 🌍 **Multi-language**: Generate translations for multiple languages
- 📝 **Documentation**: Keep translation contexts organized

## Installation

```bash
pip install babbleon-cli
```

## Quick Start

1. Initialize babbleon in your project:
```bash
babbleon init
```

2. Add languages to your configuration:
```bash
babbleon config --add-language fr
```

3. Generate translations:
```bash
babbleon translate all -o ./translations
```

## Configuration

When you run `babbleon init`, it creates a `.babbleon` directory with three files:

### 1. `babbleon.config.yaml`
```yaml
files:
  reference: reference.yaml  # Source translations file
  docs: docs.md             # Documentation file
languages:
  - en                      # Default languages
  - ko
  - vi
```

### 2. `reference.yaml`
Your source translations in YAML format:
```yaml
# Example structure
welcome:
  title: "Welcome to our app!"
  subtitle: "Get started by..."
errors:
  not_found: "Page not found"
```

### 3. `docs.md`
Documentation for translators:
```markdown
# Translation Documentation

## Welcome Screen
- `welcome.title`: Main welcome message on the landing page
- `welcome.subtitle`: Secondary text below the welcome message

## Error Messages
- `errors.not_found`: Shown when a page cannot be found
```

## Commands

### Config Management
```bash
# Add a language
babbleon config --add-language fr

# Remove a language
babbleon config --remove-language fr

# List configured languages
babbleon config --list-languages
```

### Validation
```bash
# Validate all documentation references
babbleon validate docs

# Validate specific reference
babbleon validate ref welcome.title
```

### Translation Generation
```bash
# Generate for specific language
babbleon translate generate fr -o fr.json

# Generate for all languages
babbleon translate all -o ./translations
```

## CLI Reference

### `babbleon init`
Initializes the babbleon configuration in your project.

### `babbleon config`
| Option | Description |
|--------|-------------|
| `--add-language CODE` | Add a language code |
| `--remove-language CODE` | Remove a language code |
| `--list-languages` | Show configured languages |

### `babbleon validate`
| Command | Description |
|---------|-------------|
| `docs` | Validate all docs references |
| `ref PATH` | Validate specific reference path |

### `babbleon translate`
| Command | Description |
|---------|-------------|
| `generate LANG [-o FILE]` | Generate translation for language |
| `all -o DIR` | Generate all translations |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.