# Universal CLI Design Specification

A comprehensive command line interface template that provides standardized support for commands, subcommands, complex configurations, profiles management, and multi-level configuration files.

## Overview

This CLI tool framework is designed to:
- Support commands, subcommands, options/parameters, and flags
- Manage complex dependencies through named profiles
- Handle configuration at global, local, and named file levels
- Provide flexible configuration file management
- Present information with colorful, readable output
- Offer comprehensive help and schema documentation

## Command Structure

```
cli-tool [COMMAND] [SUBCOMMAND] [OPTIONS] [FLAGS]
```

## Core Commands

The tool supports the following primary commands:

- `config`: Manage configuration files (global, local, named)
- `profile`: Manage profiles for complex dependencies
- `llm`: Specific implementation of profile management for LLMs
- `help`: Display help information
- `schema`: Display command structure as ASCII art

## Profile Management

Profiles provide a way to manage complex dependencies with multiple parameters. The general syntax for profile management is:

```
cli-tool [TYPE] [ACTION] [OPTIONS] [CONFIG-SCOPE]
```

Where:
- `[TYPE]`: The type of profile (e.g., `llm`, `database`, `api`)
- `[ACTION]`: The action to perform (`create`, `list`, `edit`, `delete`, `use`, `show`)
- `[OPTIONS]`: Profile-specific options and parameters
- `[CONFIG-SCOPE]`: Where to apply the action (`--global`, `--local`, `--file <filepath>`)

### LLM Profile Example

```
cli-tool llm create --name "gpt4-standard" --provider "openai" --model "gpt-4" --api-key "key123" --temperature 0.7 --global
cli-tool llm list --local
cli-tool llm use --name "gpt4-standard"
cli-tool llm show --name "claude-opus" --file "~/my-configs/ai-tools.json"
```

JSON-based creation and editing is also supported:

```
cli-tool llm create '{"name": "gpt4-standard", "provider": "openai", "model": "gpt-4", "api_key": "key123", "temperature": 0.7}' --global
cli-tool llm edit '{"name": "gpt4-standard", "temperature": 0.5}' --global
```

## Configuration Management

The tool supports three levels of configuration files:

1. **Global**: System-wide settings stored in `~/.cli-tool/config.json`
2. **Local**: Project-specific settings stored in `./.cli-tool/config.json`
3. **Named**: User-specified configuration files at any location

Configuration management commands allow working with these files:

```
cli-tool config [ACTION] [CONFIG-SCOPE] [OPTIONS]
```

### Configuration Actions

- `show`: Display configuration content
- `save`: Save current parameters to configuration
- `update`: Update configuration with current parameters
- `replace`: Replace entire configuration with current parameters
- `import`: Import configuration from another file
- `export`: Export configuration to another file
- `reset`: Reset configuration to defaults
- `generate`: Generate command-line instructions based on configuration

### Config Examples

```
cli-tool config show --global
cli-tool config save --local
cli-tool config update --file "~/my-configs/special.json"
cli-tool config import --from-file "~/my-configs/special.json" --to-global
cli-tool config export --from-local --to-file "~/my-configs/special.json"
cli-tool config generate --local
```

## Configuration Hierarchy

When resolving parameters, the tool uses the following precedence (highest to lowest):

1. Command line arguments
2. Named configuration (if specified with `--file`)
3. Local configuration
4. Global configuration
5. Default values

## LLM Profile Structure

LLM profiles use the following JSON structure:

```json
{
  "name": "profile-name",
  "provider": "openai",
  "model": "gpt-4",
  "deployment": "deployment-name",
  "api_key": "YOUR_API_KEY",
  "base_url": "https://api.openai.com",
  "api_version": "v1",
  "temperature": 0.7
}
```

## Complete Configuration File Structure

The configuration files use the following JSON structure:

```json
{
  "profiles": {
    "llm": {
      "profile-name-1": {
        "name": "profile-name-1",
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "YOUR_API_KEY",
        "base_url": "https://api.openai.com",
        "api_version": "v1",
        "temperature": 0.3
      },
      "profile-name-2": {
        "name": "profile-name-2",
        "provider": "anthropic",
        "model": "claude-3-opus",
        "api_key": "YOUR_API_KEY",
        "base_url": "https://api.anthropic.com",
        "api_version": "v1",
        "temperature": 0.7
      }
    },
    "database": {
      "postgres-dev": {
        "name": "postgres-dev",
        "type": "postgres",
        "host": "localhost",
        "port": 5432,
        "username": "dev_user",
        "password": "password",
        "database": "dev_db"
      }
    }
  },
  "defaults": {
    "llm": "profile-name-1",
    "database": "postgres-dev"
  },
  "settings": {
    "output_format": "json",
    "color_theme": "dark",
    "log_level": "info"
  }
}
```

## Help Documentation

The tool provides comprehensive help information:

```
cli-tool help
cli-tool help config
cli-tool help llm
cli-tool help llm create
```

## Schema Visualization

The schema command presents a complete map of commands, options, and features as a colorful ASCII tree:

```
cli-tool schema
cli-tool schema --verbose
cli-tool schema config
cli-tool schema llm
```

## Colorful Output

All output is colorized for improved readability:

- **Commands**: Bright cyan
- **Subcommands**: Blue
- **Options**: Green
- **Values**: White
- **Success messages**: Green
- **Warnings**: Yellow
- **Errors**: Red
- **Schema structure**: Multiple colors following a standardized scheme

## Usage Examples

### Creating and Using LLM Profiles

```bash
# Create a new LLM profile in the global configuration
cli-tool llm create --name "gpt4-standard" --provider "openai" --model "gpt-4" --api-key "key123" --temperature 0.7 --global

# Create a profile with JSON input
cli-tool llm create '{"name": "claude-opus", "provider": "anthropic", "model": "claude-3-opus", "api_key": "key456", "temperature": 0.5}' --local

# List all globally available LLM profiles
cli-tool llm list --global

# Use a specific LLM profile
cli-tool llm use --name "gpt4-standard"

# Show details of a specific profile
cli-tool llm show --name "claude-opus"

# Edit a profile parameter
cli-tool llm edit --name "gpt4-standard" --temperature 0.5 --global

# Delete a profile
cli-tool llm delete --name "old-profile" --global
```

### Working with Configuration Files

```bash
# Show content of the local configuration file
cli-tool config show --local

# Show content of a named configuration file
cli-tool config show --file "~/my-configs/special.json"

# Save current parameters to global configuration
cli-tool config save --global

# Update global configuration with local values
cli-tool config import --from-local --to-global

# Update local configuration with global values
cli-tool config import --from-global --to-local

# Replace local configuration with a named file
cli-tool config import --from-file "~/my-configs/special.json" --to-local --replace

# Generate command-line instructions from configuration
cli-tool config generate --file "~/my-configs/special.json"
```

### Using Help and Schema

```bash
# Show general help
cli-tool help

# Show help for a specific command
cli-tool help llm create

# Show complete command schema
cli-tool schema

# Show detailed schema for a specific command
cli-tool schema llm --verbose
```

## Implementation Recommendations

1. Use a library like `rich` or `colorama` for colorful terminal output
2. Implement a layered configuration system with proper precedence rules
3. Use a modular design to allow easy addition of new profile types
4. Provide comprehensive error handling with helpful error messages
5. Support environment variables for sensitive information (e.g., API keys)
6. Include auto-completion scripts for common shells
7. Support both POSIX and GNU-style command-line argument formats
8. Provide a plugin system for extending functionality
9. Implement configuration validation to prevent invalid settings
10. Include logging capabilities with configurable verbosity levels

## Schema Visual Representation

When running `cli-tool schema`, the output should look like:

```
[BRIGHT CYAN]cli-tool[/BRIGHT CYAN]
│
├── [YELLOW]COMMANDS[/YELLOW]
│   ├── [CYAN]config[/CYAN]                [WHITE]Manage configuration files[/WHITE]
│   │   ├── [BLUE]show[/BLUE]              [WHITE]Display configuration content[/WHITE]
│   │   ├── [BLUE]save[/BLUE]              [WHITE]Save parameters to configuration[/WHITE]
│   │   ├── [BLUE]update[/BLUE]            [WHITE]Update configuration with parameters[/WHITE]
│   │   ├── [BLUE]replace[/BLUE]           [WHITE]Replace entire configuration[/WHITE]
│   │   ├── [BLUE]import[/BLUE]            [WHITE]Import from another configuration[/WHITE]
│   │   ├── [BLUE]export[/BLUE]            [WHITE]Export to another configuration[/WHITE]
│   │   ├── [BLUE]reset[/BLUE]             [WHITE]Reset configuration to defaults[/WHITE]
│   │   └── [BLUE]generate[/BLUE]          [WHITE]Generate command-line from config[/WHITE]
│   │
│   ├── [CYAN]profile[/CYAN]               [WHITE]Manage dependency profiles[/WHITE]
│   │   ├── [BLUE]create[/BLUE]            [WHITE]Create a new profile[/WHITE]
│   │   ├── [BLUE]list[/BLUE]              [WHITE]List available profiles[/WHITE]
│   │   ├── [BLUE]edit[/BLUE]              [WHITE]Edit an existing profile[/WHITE]
│   │   ├── [BLUE]delete[/BLUE]            [WHITE]Delete a profile[/WHITE]
│   │   ├── [BLUE]use[/BLUE]               [WHITE]Use a specific profile[/WHITE]
│   │   └── [BLUE]show[/BLUE]              [WHITE]Show profile details[/WHITE]
│   │
│   ├── [CYAN]llm[/CYAN]                   [WHITE]Manage LLM profiles[/WHITE]
│   │   ├── [BLUE]create[/BLUE]            [WHITE]Create a new LLM profile[/WHITE]
│   │   ├── [BLUE]list[/BLUE]              [WHITE]List available LLM profiles[/WHITE]
│   │   ├── [BLUE]edit[/BLUE]              [WHITE]Edit an existing LLM profile[/WHITE]
│   │   ├── [BLUE]delete[/BLUE]            [WHITE]Delete an LLM profile[/WHITE]
│   │   ├── [BLUE]use[/BLUE]               [WHITE]Use a specific LLM profile[/WHITE]
│   │   └── [BLUE]show[/BLUE]              [WHITE]Show LLM profile details[/WHITE]
│   │
│   ├── [CYAN]help[/CYAN]                  [WHITE]Display help information[/WHITE]
│   └── [CYAN]schema[/CYAN]                [WHITE]Display command structure tree[/WHITE]
│
├── [YELLOW]CONFIG SCOPE FLAGS[/YELLOW]
│   ├── [GREEN]--global[/GREEN]            [WHITE]Use global configuration[/WHITE]
│   ├── [GREEN]--local[/GREEN]             [WHITE]Use local configuration[/WHITE]
│   └── [GREEN]--file <PATH>[/GREEN]       [WHITE]Use named configuration file[/WHITE]
│
└── [YELLOW]GLOBAL OPTIONS[/YELLOW]
    ├── [GREEN]--help, -h[/GREEN]          [WHITE]Show help message[/WHITE]
    ├── [GREEN]--verbose, -v[/GREEN]       [WHITE]Enable verbose output[/WHITE]
    └── [GREEN]--quiet, -q[/GREEN]         [WHITE]Suppress non-essential output[/WHITE]
```

## LLM Command Schema

When running `cli-tool schema llm`, the output should look like:

```
[BRIGHT CYAN]cli-tool llm[/BRIGHT CYAN]
│
├── [YELLOW]SUBCOMMANDS[/YELLOW]
│   ├── [BLUE]create[/BLUE]                [WHITE]Create a new LLM profile[/WHITE]
│   │   ├── [GREEN]--name <NAME>[/GREEN]   [WHITE]Profile name[/WHITE]
│   │   ├── [GREEN]--provider <PROV>[/GREEN] [WHITE]LLM provider[/WHITE]
│   │   ├── [GREEN]--model <MODEL>[/GREEN] [WHITE]Model name[/WHITE]
│   │   ├── [GREEN]--deployment <DEPL>[/GREEN] [WHITE]Deployment name[/WHITE]
│   │   ├── [GREEN]--api-key <KEY>[/GREEN] [WHITE]API key[/WHITE]
│   │   ├── [GREEN]--base-url <URL>[/GREEN] [WHITE]Base URL for API[/WHITE]
│   │   ├── [GREEN]--api-version <VER>[/GREEN] [WHITE]API version[/WHITE]
│   │   └── [GREEN]--temperature <TEMP>[/GREEN] [WHITE]Temperature (0.0-1.0)[/WHITE]
│   │
│   ├── [BLUE]list[/BLUE]                  [WHITE]List available LLM profiles[/WHITE]
│   │   └── [GREEN]--format <FORMAT>[/GREEN] [WHITE]Output format (json, table)[/WHITE]
│   │
│   ├── [BLUE]edit[/BLUE]                  [WHITE]Edit an existing LLM profile[/WHITE]
│   │   ├── [GREEN]--name <NAME>[/GREEN]   [WHITE]Profile name[/WHITE]
│   │   └── [GREEN]<same options as create>[/GREEN]
│   │
│   ├── [BLUE]delete[/BLUE]                [WHITE]Delete an LLM profile[/WHITE]
│   │   └── [GREEN]--name <NAME>[/GREEN]   [WHITE]Profile name[/WHITE]
│   │
│   ├── [BLUE]use[/BLUE]                   [WHITE]Use a specific LLM profile[/WHITE]
│   │   └── [GREEN]--name <NAME>[/GREEN]   [WHITE]Profile name[/WHITE]
│   │
│   └── [BLUE]show[/BLUE]                  [WHITE]Show LLM profile details[/WHITE]
│       ├── [GREEN]--name <NAME>[/GREEN]   [WHITE]Profile name[/WHITE]
│       └── [GREEN]--format <FORMAT>[/GREEN] [WHITE]Output format (json, yaml, table)[/WHITE]
│
└── [YELLOW]CONFIG SCOPE FLAGS[/YELLOW]
    ├── [GREEN]--global[/GREEN]            [WHITE]Use global configuration[/WHITE]
    ├── [GREEN]--local[/GREEN]             [WHITE]Use local configuration[/WHITE]
    └── [GREEN]--file <PATH>[/GREEN]       [WHITE]Use named configuration file[/WHITE]
```