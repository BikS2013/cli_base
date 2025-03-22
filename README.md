# Universal CLI Tool

A comprehensive command-line interface template that provides standardized support for commands, subcommands, complex configurations, profiles management, and multi-level configuration files.

## Features

- Support for commands, subcommands, options/parameters, and flags
- Management of complex dependencies through named profiles
- Configuration handling at global, local, and named file levels
- Flexible configuration file management
- Colorful, readable output
- Comprehensive help and schema documentation

## Installation

```
pip install -e .
```

## Usage

The CLI tool follows this general structure:

```
cli-tool [COMMAND] [SUBCOMMAND] [OPTIONS] [FLAGS]
```

### Core Commands

- `config`: Manage configuration files (global, local, named)
- `llm`: Manage LLM profiles
- `schema`: Display command structure as ASCII art
- `help`: Display help information

### Configuration Management

The tool supports three levels of configuration files:

1. **Global**: System-wide settings stored in `~/.cli-tool/config.json`
2. **Local**: Project-specific settings stored in `./.cli-tool/config.json`
3. **Named**: User-specified configuration files at any location

Configuration actions include:

```bash
# Show content of the local configuration file
cli-tool config show --local

# Save current parameters to global configuration
cli-tool config save --global

# Import configuration from another file
cli-tool config import --from-file "~/my-configs/special.json" --to-local
```

### LLM Profile Management

Create and manage LLM profiles:

```bash
# Create a new LLM profile
cli-tool llm create --name "gpt4-standard" --provider "openai" --model "gpt-4" --api-key "key123" --temperature 0.7 --global

# List all LLM profiles
cli-tool llm list --global

# Show a specific profile
cli-tool llm show --name "gpt4-standard"

# Set a profile as default
cli-tool llm use --name "gpt4-standard"
```

### Schema and Help

View the command structure and get help:

```bash
# Show schema
cli-tool schema show

# Get detailed help
cli-tool help
cli-tool help config
cli-tool help llm create
```

## Development

This CLI tool is built using:

- [Click](https://click.palletsprojects.com/): For command-line interface creation
- [Rich](https://rich.readthedocs.io/): For colorful terminal output
- Python 3.11+

## License

This project is licensed under the MIT License.