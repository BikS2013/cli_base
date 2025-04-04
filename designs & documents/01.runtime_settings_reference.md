# Runtime Settings System Reference

This document provides a comprehensive reference for the runtime settings system used in the CLI tool. The system manages configuration files across different scopes (global, local, and file-specific), handles parameter resolution, and provides access to profiles and other configuration settings.

## Overview

The runtime settings system is built around two primary components:

1. **ContextManager** - A singleton that manages runtime context and settings
2. **AdvancedRTSettings** - A class that handles configuration loading, parameter resolution, and profile management

The system supports three configuration scopes with precedence:

1. **File** - Named configuration file specified with `--file PATH`
2. **Local** - Project-specific configuration in current directory (`./.cli-tool/config.json`) 
3. **Global** - User-level configuration in home directory (`~/.cli-tool/config.json`)

## AdvancedRTSettings Class

The `AdvancedRTSettings` class is the core component for runtime settings management.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `global_config_dir` | `Path` | Path to global configuration directory (`~/.cli-tool`) |
| `global_config_path` | `Path` | Path to global configuration file (`~/.cli-tool/config.json`) |
| `local_config_dir` | `Path` | Path to local configuration directory (`./.cli-tool`) |
| `local_config_path` | `Path` | Path to local configuration file (`./.cli-tool/config.json`) |
| `named_config_path` | `Path` | Path to named configuration file (if specified) |
| `global_config` | `Dict` | Global configuration content |
| `local_config` | `Dict` | Local configuration content |
| `named_config` | `Dict` | Named configuration content (if specified) |
| `cli_args` | `Dict` | Command-line arguments |
| `verbose` | `bool` | Verbose output flag |
| `quiet` | `bool` | Quiet output flag |
| `context` | `Dict` | Runtime context with merged configuration |
| `command_context` | `Dict` | Information about the current command |

### Methods

#### Basic Configuration Management

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_config_path(scope)` | `scope: str` | `Path` | Get the configuration file path for the specified scope |
| `get_config(scope)` | `scope: str` | `Dict` | Get the configuration for the specified scope |
| `save_config(config, scope)` | `config: Dict`, `scope: str` | `None` | Save configuration to the specified scope |
| `update_config(updates, scope)` | `updates: Dict`, `scope: str` | `Dict` | Update configuration with new values, preserving existing structure |
| `get_effective_config()` | None | `Dict` | Get the effective configuration considering all precedence rules |
| `to_json(include_paths, include_configs, include_context, include_cli_args)` | `include_paths: bool`, `include_configs: bool`, `include_context: bool`, `include_cli_args: bool` | `Dict` | Produce a complete JSON representation of the current state |

#### Profile Management

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_profile(profile_type, name)` | `profile_type: str`, `name: str` | `Dict` | Get a specific profile from the effective configuration |
| `get_profile_from_any_scope(profile_type, name)` | `profile_type: str`, `name: str` | `Dict` | Get a specific profile from any available scope |
| `get_profiles(profile_type, scope=None)` | `profile_type: str`, `scope: str` | `Dict` | Get all profiles of a specific type, optionally filtered by scope |
| `get_default_profile(profile_type)` | `profile_type: str` | `str` | Get the name of the default profile for a specific type |
| `get_default_profile_from_any_scope(profile_type)` | `profile_type: str` | `str` | Get the name of the default profile from any scope |
| `set_default_profile(profile_type, name, scope)` | `profile_type: str`, `name: str`, `scope: str` | `None` | Set a profile as the default for its type in the specified scope |
| `create_profile(profile_type, profile, scope)` | `profile_type: str`, `profile: Dict`, `scope: str` | `None` | Create a new profile in the specified configuration |
| `edit_profile(profile_type, name, updates, scope)` | `profile_type: str`, `name: str`, `updates: Dict`, `scope: str` | `Dict` | Edit an existing profile in the configuration |
| `delete_profile(profile_type, name, scope)` | `profile_type: str`, `name: str`, `scope: str` | `None` | Delete a profile from the configuration |

#### Settings and Command Configuration

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_setting(setting_name, default=None)` | `setting_name: str`, `default: Any` | `Any` | Get a setting value from the effective configuration |
| `set_setting(setting_name, value, scope)` | `setting_name: str`, `value: Any`, `scope: str` | `None` | Set a setting value in the specified scope |
| `get_command_config(command_path=None)` | `command_path: str` | `Dict` | Get command-specific configuration settings |
| `get_param_value(param_name, default=None)` | `param_name: str`, `default: Any` | `Any` | Get a parameter value from the most appropriate source |
| `set_command_config(command_path, config, scope)` | `command_path: str`, `config: Dict`, `scope: str` | `None` | Set command-specific configuration settings |
| `update_command_config(command_path, updates, scope)` | `command_path: str`, `updates: Dict`, `scope: str` | `Dict` | Update command-specific configuration settings |
| `delete_command_config(command_path, scope)` | `command_path: str`, `scope: str` | `None` | Delete command-specific configuration settings |

### Internal Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `_initialize_config_files()` | None | `None` | Create default config directories and files if they don't exist |
| `_load_configurations()` | None | `None` | Load all configuration files according to precedence rules |
| `_build_runtime_context()` | None | `None` | Build the runtime context by merging configurations |
| `_get_command_context()` | None | `Dict` | Get information about the current command context |
| `_apply_command_specific_config()` | None | `None` | Apply command-specific configurations to the runtime context |
| `_deep_merge(dict1, dict2)` | `dict1: Dict`, `dict2: Dict` | `Dict` | Deep merge two dictionaries (static method) |

## ContextManager Class

The `ContextManager` class is a singleton that manages the runtime context and settings.

### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_instance()` | None | `ContextManager` | Get the singleton instance (static method) |
| `initialize(options=None)` | `options: Dict` | `ContextManager` | Initialize the context with the given options (static method) |
| `reset()` | None | `None` | Reset the singleton instance (static method) |
| `get_settings()` | None | `AdvancedRTSettings` | Get the current settings instance |

## Helper Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `initialize_context(options=None)` | `options: Dict` | `ContextManager` | Initialize the context with the given options |
| `get_parameter_value(param_name, default=None)` | `param_name: str`, `default: Any` | `Any` | Get a parameter value from the context |

## Usage Patterns

### Configuration Management

```python
# Initialize context with scope options
ctx = initialize_context({"scope": "global"})
rt = ctx.settings

# Get and modify configuration
config = rt.get_config("global")
config["settings"]["output_format"] = "table"
rt.save_config(config, "global")

# Update configuration with new values
updates = {"settings": {"log_level": "debug"}}
rt.update_config(updates, "global")
```

### Profile Management

```python
# Create a new profile
new_profile = {
    "name": "my-llm",
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
}
rt.create_profile("llm", new_profile, "local")

# Set as default
rt.set_default_profile("llm", "my-llm", "local")

# Get profile
profile = rt.get_profile("llm", "my-llm")
```

### Parameter Resolution

```python
# Get a parameter value with fallback
temperature = rt.get_param_value("temperature", 0.5)

# Get a setting
output_format = rt.get_setting("output_format", "json")
```

### Command-Specific Configuration

```python
# Set command configuration
cmd_config = {
    "stream": True,
    "temperature": 0.8
}
rt.set_command_config("generate.prompt", cmd_config, "local")

# Get command configuration
config = rt.get_command_config("generate.prompt")
```

### JSON Representation

```python
# Get complete JSON representation
status_json = rt.to_json(
    include_paths=True,
    include_configs=True,
    include_context=True,
    include_cli_args=True
)
```

## JSON Output Structure

The `to_json()` method returns a structured JSON representation with the following format:

```json
{
    "current_scope": "local",
    "verbose": true,
    "quiet": false,
    
    "config_status": {
        "global_exists": true,
        "local_exists": true,
        "named_exists": false
    },
    
    "command_context": {
        "command_path": "config.show",
        "command_name": "show",
        "parent_commands": ["config"],
        "root_command": "cli"
    },
    
    "sys_argv": ["cli-tool", "config", "show", "--verbose"],
    
    "cli_args": {
        "scope": "local",
        "verbose": true
    },
    
    "paths": {
        "global_config_dir": "/home/user/.cli-tool",
        "global_config_path": "/home/user/.cli-tool/config.json",
        "local_config_dir": "/project/.cli-tool",
        "local_config_path": "/project/.cli-tool/config.json"
    },
    
    "effective_config": {
        "settings": {
            "output_format": "json",
            "color_theme": "dark",
            "log_level": "info"
        },
        "defaults": {
            "llm": "my-llm",
            "database": null
        },
        "profile_names": {
            "llm": ["my-llm", "gpt4"],
            "database": []
        }
    },
    
    "raw_configs": {
        "global": { /* raw global config */ },
        "local": { /* raw local config */ }
    }
}
```

## Configuration File Format

The configuration files use a standardized JSON format:

```json
{
    "profiles": {
        "llm": {
            "profile-name": {
                "name": "profile-name",
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 2000,
                "api_key": "sk-..."
            }
        },
        "database": {
            ...
        }
    },
    "defaults": {
        "llm": "profile-name",
        "database": null
    },
    "settings": {
        "output_format": "json",
        "color_theme": "dark",
        "log_level": "info"
    },
    "commands": {
        "generate.prompt": {
            "stream": true,
            "temperature": 0.8
        }
    }
}
```

## Dependencies

The runtime settings system has the following dependencies:

1. **Click** - For command-line interface
2. **ParameterResolver** - For resolving command parameters
3. **OutputFormatter** - For formatting output with color and structure

## Function Call Flow

1. `initialize_context()` is called from the `standard_command` decorator
2. The `ContextManager` singleton is initialized
3. `AdvancedRTSettings` is created with CLI arguments
4. Configuration files are loaded from all scopes
5. Runtime context is built by merging configurations according to precedence rules
6. Command-specific configurations are applied
7. Command execution proceeds with the initialized context
8. `OutputFormatter.end_command_with_runtime_settings()` is called at the end of commands to display runtime settings in verbose mode

## Best Practices

1. **Always use the `standard_command` decorator** for commands that need access to configuration
2. **Check for verbose mode** before displaying detailed output
3. **Use `get_param_value()`** to get parameter values, as it handles precedence correctly
4. **Validate scope and file_path combinations** in commands that modify configuration
5. **Include error handling** for configuration loading and saving operations
6. **Use `to_json()` with appropriate flags** to get a focused view of the runtime settings
7. **Always display runtime settings when verbose mode is enabled** by calling `OutputFormatter.end_command_with_runtime_settings()`