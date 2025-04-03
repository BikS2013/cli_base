# Standard Command Decorator

This document describes the `standard_command` decorator that provides a unified approach to implementing commands in the CLI tool.

## Overview

The `standard_command` decorator combines several common patterns for CLI commands:

1. Adds configuration scope options (`--global`, `--local`, `--file`)
2. Initializes the context with scope parameters
3. Resolves parameters via the parameter resolver

This approach significantly reduces boilerplate code and ensures consistent behavior across all commands.

## Usage

### Basic Usage

```python
@standard_command()
@command_group.command("name")
def my_command(scope: Optional[str] = None, file_path: Optional[str] = None):
    """Command description."""
    # Context is already initialized by standard_command
    ctx = ContextManager.get_instance()
    rt = ctx.settings
    
    # Command implementation...
```

### With Optional Context Initialization

```python
@standard_command(init_context=False)
@command_group.command("name")
def my_command(scope: Optional[str] = None, file_path: Optional[str] = None):
    """Command description."""
    # You need to initialize context manually
    ctx = ContextManager.initialize({"scope": scope, "file_path": file_path})
    
    # Command implementation...
```

## Decorator Order

The order of decorators is important. The standard pattern is:

```python
@standard_command()
@command_group.command("name")
@click.option("--my-option", help="Option description")
@click.argument("arg_name")
def my_command(...):
    """Command description."""
    # Implementation...
```

The decorators are applied from bottom to top, so `standard_command()` must be first (outermost) to ensure proper parameter handling.

## Benefits

- Reduces boilerplate code in command implementations
- Ensures consistent parameter handling across all commands
- Handles configuration scope options automatically
- Properly initializes the context for command execution
- Resolves parameters from all sources (CLI args, config files, etc.)

## Implementation Details

The decorator:

1. Applies the `scope_options` decorator to add scope options (`--global`, `--local`, `--file`)
2. Extracts scope parameters from the command arguments
3. Checks command-line arguments directly for scope flags as a fallback
4. Initializes the context with the scope parameters
5. Applies parameter resolution through the `with_resolved_params` decorator

This ensures that all commands using this decorator will have consistent handling of configuration scopes and parameter resolution.

## Example Commands

Commands that use the `standard_command` decorator:

```python
# Config commands
@standard_command()
@config_group.command(name="show")
def show_config(scope: Optional[str] = None, file_path: Optional[str] = None):
    """Display configuration content."""
    # Context is already initialized
    ctx = ContextManager.get_instance()
    # Implementation...

# LLM commands
@standard_command()
@generate_group.command("prompt")
@click.argument("prompt", type=str)
@click.option("--profile", "-p", help="LLM profile to use")
def generate_prompt(prompt: str, profile: Optional[str] = None,
                   scope: Optional[str] = None, file_path: Optional[str] = None):
    """Generate a response from an LLM using the given prompt."""
    # Context is already initialized
    # Implementation...
```