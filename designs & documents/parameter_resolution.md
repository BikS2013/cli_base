# Parameter Resolution

This document explains the parameter resolution system, which completely decouples parameter retrieval and validation from command execution.

## Overview

The parameter resolution system is designed to:

1. Resolve all parameters for a command before execution
2. Handle parameters from various sources (CLI args, config files, defaults)
3. Apply precedence rules correctly
4. Validate and prepare parameters for command use
5. Decouple parameter handling from command logic

## Key Components

### ParameterResolver Class

The `ParameterResolver` class centralizes all parameter resolution logic:

```python
class ParameterResolver:
    """
    Handles the resolution of parameters for CLI commands.
    
    This class is responsible for retrieving and validating all required parameters
    for command execution from various sources (CLI args, config files, etc.)
    before the actual command execution.
    """
```

### with_resolved_params Decorator

The `with_resolved_params` decorator makes it easy to apply parameter resolution to any command:

```python
@with_resolved_params
def my_command(param1, param2, ...):
    # Command implementation using resolved parameters
    ...
```

### resolve_params Utility Function

The `resolve_params` function can be called directly to resolve parameters without using the decorator:

```python
def some_command():
    # Resolve parameters
    params = resolve_params()
    
    # Use resolved parameters
    ...
```

## Parameter Resolution Flow

When a command is executed, parameters are resolved in this order:

1. **Command-line arguments**: Parameters explicitly provided by the user (highest priority)
2. **Configuration values**: Command-specific parameters from configuration files
3. **Default values**: Default values specified in the command definition

### Configuration Scope Parameters

Scope parameters (`--global`, `--local`, `--file`) are processed first to determine which configuration files to use:

```python
# Extract scope parameters
scope_params = resolver._extract_scope_params(params)

# Initialize context with scope parameters
_initialize_context(scope_params)
```

### Command-Specific Configuration

Commands can have specific default parameter values stored in configuration:

```json
{
  "commands": {
    "generate.prompt": {
      "stream": true,
      "temperature": 0.7
    }
  }
}
```

The resolver extracts the full command path and looks for matching configuration:

```python
# Get command path (e.g., "generate.prompt")
command_path = resolver._get_command_path(ctx)

# Get command-specific parameters
config_params = resolver._get_config_params_for_command(effective_config, command_path)
```

### Special Parameter Resolution

Some parameters require special handling, such as profile references:

```python
# Handle profile parameters
if "profile" in params and params["profile"] is None:
    # For LLM commands, try to resolve the profile
    if command_path.startswith("generate") or command_path.startswith("llm"):
        default_profile = resolver._get_default_profile("llm", config)
        if default_profile:
            params["profile"] = default_profile
```

## Example Usage

### 1. Adding the Decorator to a Command

```python
@click.command()
@click.argument("input_file")
@click.option("--format", type=click.Choice(["json", "yaml"]), default="json")
@global_scope_options
@with_resolved_params
def process_file(input_file, format, scope=None, file_path=None):
    """Process a file with specified format."""
    # No need to manually initialize context or resolve parameters
    # Just use the parameters directly
    ...
```

### 2. Using the Direct Function Call

```python
@click.command()
@click.argument("name")
@global_scope_options
def create_profile(name, scope=None, file_path=None):
    """Create a new profile."""
    # Manually resolve parameters
    params = resolve_params()
    
    # Use resolved parameters
    profile_type = params.get("type", "default")
    ...
```

## Command-Specific Configuration

You can set command-specific default parameters in the configuration files:

### Global Configuration

```json
{
  "commands": {
    "generate.prompt": {
      "stream": true,
      "temperature": 0.7,
      "max_tokens": 2000
    },
    "generate.chat": {
      "stream": true
    }
  }
}
```

### Local Configuration

```json
{
  "commands": {
    "generate.prompt": {
      "temperature": 0.9  // Overrides global setting
    }
  }
}
```

## Benefits

1. **Cleaner Command Logic**: Commands focus on their core functionality, not parameter parsing
2. **Consistent Parameter Handling**: All parameters are resolved the same way across commands
3. **Configuration Support**: Parameters can be stored in configuration files
4. **Validation Before Execution**: Parameters are validated before the command runs
5. **Reduced Duplication**: Common parameter resolution logic is centralized

## Technical Details

### Parameter Precedence Rules

1. Command-line arguments (highest priority)
2. Named configuration parameters (if using `--file`)
3. Local configuration parameters (if using `--local` or default)
4. Global configuration parameters
5. Command default values (lowest priority)

### Command Path Resolution

The full command path is used to look up command-specific configuration:

- `generate` -> `generate`
- `generate prompt` -> `generate.prompt`
- `llm create` -> `llm.create`

This allows storing different default values for different subcommands.

### Decorator Behavior

The `with_resolved_params` decorator:

1. Gets the current Click context
2. Creates a ParameterResolver instance
3. Resolves all parameters
4. Updates the kwargs with resolved values
5. Calls the original function with updated kwargs

## Conclusion

The parameter resolution system provides a clean separation between parameter handling and command logic. It makes commands simpler and more focused, while ensuring consistent parameter resolution across the entire CLI tool.