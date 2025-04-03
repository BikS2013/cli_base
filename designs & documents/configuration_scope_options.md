# Configuration Scope Options

This document describes the configuration scope options (`--global`, `--local`, and `--file`) that can be used with any command in the CLI tool.

## Overview

The CLI tool supports multiple configuration scopes to provide flexibility in how settings are loaded and applied. 
This allows users to work with different configurations for different projects or purposes.

Configuration scope options work uniformly across ALL commands, making it possible to use different configuration files 
or scope with any command in the tool.

## Available Configuration Scope Options

### `--global`

```
cli-tool [command] --global
```

- Uses only the global configuration (located at `~/.cli-tool/config.json`)
- Ignores local configuration entirely
- Useful for commands that should apply the same settings across all projects

### `--local`

```
cli-tool [command] --local
```

- Uses local configuration (`.cli-tool/config.json` in the current directory)
- Falls back to global configuration for settings not defined locally
- This is the default behavior if no scope option is specified

### `--file <path>`

```
cli-tool [command] --file /path/to/custom-config.json
```

- Uses the specified custom configuration file
- For any settings not found in the custom file, falls back to local configuration
- If settings are still missing, falls back to global configuration
- Useful for one-off commands with special configuration needs

## Profile Resolution

Profiles (like LLM profiles) are resolved using the same precedence rules as general configuration. When looking for a profile:

1. First, the tool looks in the highest priority configuration scope (based on which flag you used)
2. If not found, it automatically checks lower priority scopes

This means:
- With `--file`, it checks: custom file → local config → global config
- With `--local` (or no option), it checks: local config → global config
- With `--global`, it only checks global config

This ensures that profiles created in global configuration can be used by any command without having to duplicate them in local configuration files.

## Precedence Rules

When multiple configuration scopes are available, the tool follows these precedence rules:

1. If `--file` option is used:
   - Command line arguments
   - Named configuration file
   - Local configuration (for missing elements)
   - Global configuration (for missing elements)
   - Default values

2. If `--local` option is used (or no option is specified):
   - Command line arguments
   - Local configuration
   - Global configuration (for missing elements)
   - Default values

3. If `--global` option is used:
   - Command line arguments
   - Global configuration
   - Default values

## Examples

### Using with any command

The configuration scope options work with ANY command in the tool:

```bash
# Use global config with generate command
cli-tool generate prompt "Why is the sky blue?" --global

# Use local config with generate command
cli-tool generate prompt "Why is the sky blue?" --local

# Use custom config file with generate command
cli-tool generate prompt "Why is the sky blue?" --file .working-local.json

# Configure a profile in a specific config file
cli-tool llm create --name "my-model" --provider "openai" --model "gpt-4" --file .working-local.json

# Run the chat command with a custom config
cli-tool generate chat --file .my-project-config.json
```

## Implementation Details

Configuration scope options are:

1. Parsed from command-line arguments
2. Applied to the runtime context
3. Used to determine which configuration files to load and in what order
4. Applied consistently across all commands in the tool

This unified approach ensures that configuration scope options work consistently throughout the entire tool.