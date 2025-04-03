# Advanced Settings System

This document explains the Advanced Settings System, which extends the basic runtime settings with enhanced parameter resolution capabilities.

## Overview

The Advanced Settings System builds on the Parameter Resolution system, providing:

1. A new `AdvancedRTSettings` class that uses `ParameterResolver` for initialization
2. An `AdvancedContextManager` for managing the advanced settings
3. Command-specific configuration storage and retrieval
4. Unified parameter access with clear precedence rules

## Key Components

### AdvancedRTSettings Class

The `AdvancedRTSettings` class extends the basic `RTSettings` class with these enhancements:

```python
class AdvancedRTSettings(RTSettings):
    """
    Advanced runtime settings class that uses ParameterResolver for initialization.
    
    This class extends the base RTSettings class with advanced parameter resolution
    capabilities, allowing it to automatically resolve parameters from various sources
    based on the current Click context.
    """
```

### AdvancedContextManager Class

The `AdvancedContextManager` extends the basic `ContextManager` to work with advanced settings:

```python
class AdvancedContextManager(ContextManager):
    """
    Advanced context manager that uses AdvancedRTSettings.
    
    This class extends the base ContextManager to use AdvancedRTSettings
    for enhanced parameter resolution and command-specific configurations.
    """
```

### Utility Functions

Several utility functions make it easy to work with advanced settings:

```python
def initialize_advanced_context(cli_args: Optional[Dict[str, Any]] = None,
                              resolver: Optional[ParameterResolver] = None) -> AdvancedContextManager:
    """Initialize or get the advanced context manager instance."""
    
def get_parameter_value(param_name: str, default: Any = None) -> Any:
    """Get a parameter value from the advanced context."""
```

## Command-Specific Configuration

A key feature of the Advanced Settings System is support for command-specific configurations.

### Configuration Structure

Command-specific configurations are stored in the `commands` section of the configuration:

```json
{
  "commands": {
    "generate.prompt": {
      "stream": true,
      "temperature": 0.7
    },
    "advanced.exec": {
      "param1": "value1",
      "param2": "value2",
      "param3": 42
    }
  }
}
```

### Managing Command Configurations

The `AdvancedRTSettings` class provides methods for managing command configurations:

```python
def get_command_config(self, command_path: Optional[str] = None) -> Dict[str, Any]:
    """Get command-specific configuration settings."""
    
def set_command_config(self, command_path: str, config: Dict[str, Any], scope: str) -> None:
    """Set command-specific configuration settings."""
    
def update_command_config(self, command_path: str, updates: Dict[str, Any], scope: str) -> Dict[str, Any]:
    """Update command-specific configuration settings."""
    
def delete_command_config(self, command_path: str, scope: str) -> None:
    """Delete command-specific configuration settings."""
```

## Parameter Resolution Process

The advanced settings system resolves parameters in this order:

1. Command-line arguments (highest priority)
2. Command-specific configuration
3. General settings
4. Default values (lowest priority)

This process is encapsulated in the `get_param_value` method:

```python
def get_param_value(self, param_name: str, default: Any = None) -> Any:
    """
    Get a parameter value from the most appropriate source.
    
    This method checks for the parameter value in this order:
    1. CLI arguments
    2. Command-specific configuration
    3. General settings
    4. Provided default value
    """
```

## Command Context

The advanced settings system automatically captures the command context when initialized:

```python
self.command_context = {
    "command_path": "generate.prompt",  # Full command path
    "command_name": "prompt",           # Current command name
    "parent_commands": ["generate"],    # Parent command names
    "root_command": "cli"               # Root command name
}
```

This context information is used to look up command-specific configurations.

## Example Usage

### Initializing Advanced Context

```python
# Initialize with current CLI arguments
ctx = initialize_advanced_context({
    "scope": scope,
    "file_path": file_path
})
advanced_settings = ctx.advanced_settings
```

### Getting Parameter Values

```python
# Get parameter with fallback default
value = get_parameter_value("param_name", "default_value")

# Get multiple parameters
param1 = get_parameter_value("param1", "default1")
param2 = get_parameter_value("param2", "default2")
param3 = get_parameter_value("param3", 0)
```

### Managing Command Configurations

```python
# Get current command configuration
cmd_config = advanced_settings.get_command_config()

# Update command configuration
updates = {"param1": "new_value", "param2": 42}
advanced_settings.update_command_config("command.path", updates, "local")

# Delete command configuration
advanced_settings.delete_command_config("command.path", "local")
```

## Advanced Command Group

The Advanced Settings System includes a new command group for managing command-specific configurations:

### advanced config

```bash
# View all command configurations
cli-tool advanced config

# View specific configuration value
cli-tool advanced config param1

# Set configuration value
cli-tool advanced config param1 value1

# Set configuration in global scope
cli-tool advanced config param1 value1 --global
```

### advanced exec

```bash
# Execute with parameters from configuration
cli-tool advanced exec test-command

# Override specific parameters
cli-tool advanced exec test-command --param1=override1

# Use configuration from a specific file
cli-tool advanced exec test-command --file=custom.json
```

## Benefits Over Basic Settings

1. **Automatic Parameter Resolution**: Parameters are automatically resolved from various sources
2. **Command-Specific Configurations**: Store and retrieve configurations specific to each command
3. **Clear Precedence Rules**: Well-defined rules for parameter resolution
4. **Command Context Awareness**: Understands the current command context
5. **Simplified API**: Easy-to-use utility functions

## Implementation Details

### Extending the Base RTSettings

The `AdvancedRTSettings` class extends `RTSettings` to ensure compatibility:

```python
class AdvancedRTSettings(RTSettings):
    # Implementation details...
```

This approach maintains backward compatibility while adding new features.

### Command Path Resolution

Command paths are constructed by joining command names with dots:

- `cli generate prompt` becomes `generate.prompt`
- `cli llm create` becomes `llm.create`
- `cli advanced exec` becomes `advanced.exec`

This format allows for easy storage and retrieval of command-specific configurations.

### Parameter Type Conversion

When setting configuration values, the system attempts to convert string values to appropriate types:

- `"true"` → `True` (boolean)
- `"false"` → `False` (boolean)
- `"42"` → `42` (integer)
- `"3.14"` → `3.14` (float)
- Everything else → string

This ensures that configuration values have the correct types when retrieved.

## Activating Advanced Settings

The Advanced Settings System is implemented as an opt-in feature. There are several ways to activate it:

### Environment Variable (Easiest)

Set the `CLI_USE_ADVANCED_SETTINGS` environment variable:

```bash
# Linux/macOS
export CLI_USE_ADVANCED_SETTINGS=1

# Windows
set CLI_USE_ADVANCED_SETTINGS=1
```

### Code Modification

Uncomment the initialization line in main.py:

```python
if __name__ == "__main__":
    initialize_with_advanced_settings()  # Uncomment this line
    cli()
```

### Programmatic Activation

Call the initialization function before running any commands:

```python
from cli_base.main import initialize_with_advanced_settings

initialize_with_advanced_settings()
# Now run your commands
```

## Transition Strategy

The Advanced Settings System can coexist with the regular settings system, allowing for a gradual transition:

1. Start by activating advanced settings with the environment variable for testing
2. Update command implementations to use `get_parameter_value()` instead of direct access
3. Move command-specific configurations to the `commands` section of configuration files
4. Once all commands have been updated, make advanced settings the default

## Conclusion

The Advanced Settings System provides a powerful way to manage command-specific configurations and resolve parameters from various sources. It builds on the Parameter Resolution system to provide a complete solution for decoupling parameter handling from command execution.

By maintaining compatibility with the existing settings system, it allows for a gradual transition to the new approach without breaking existing functionality.