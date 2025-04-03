# Advanced Settings JSON Representation

This document explains the JSON representation functionality added to the `AdvancedRTSettings` class and the related `config status` command.

## Overview

The `to_json` method and `config status` command provide a comprehensive way to inspect the current state of the configuration system. This is particularly useful for:

1. Debugging configuration issues
2. Understanding how different configuration scopes are being applied
3. Verifying that command-line arguments are being properly processed
4. Inspecting the complete runtime context

## The `to_json` Method

The `to_json` method in the `AdvancedRTSettings` class produces a complete JSON representation of the current state:

```python
def to_json(self, include_paths: bool = True, include_configs: bool = True, 
           include_context: bool = True, include_cli_args: bool = True) -> Dict[str, Any]:
    """
    Produce a complete JSON representation of the current state.
    
    Args:
        include_paths: Whether to include file paths in the output
        include_configs: Whether to include raw configurations in the output
        include_context: Whether to include the runtime context in the output
        include_cli_args: Whether to include CLI arguments in the output
        
    Returns:
        Dictionary representing the complete state, ready for JSON serialization
    """
    # Implementation...
```

### Output Structure

The JSON representation includes the following sections:

1. **Basic Information**:
   - `current_scope`: The current configuration scope ("global", "local", or "file")
   - `verbose`: Whether verbose output is enabled
   - `quiet`: Whether quiet mode is enabled

2. **File Paths** (if `include_paths=True`):
   - `global_config_dir`: Path to the global configuration directory
   - `global_config_path`: Path to the global configuration file
   - `local_config_dir`: Path to the local configuration directory
   - `local_config_path`: Path to the local configuration file
   - `named_config_path`: Path to the named configuration file (if applicable)

3. **Configuration Status**:
   - `global_exists`: Whether the global configuration file exists
   - `local_exists`: Whether the local configuration file exists
   - `named_exists`: Whether the named configuration file exists (if applicable)

4. **Raw Configurations** (if `include_configs=True`):
   - `global`: The raw global configuration
   - `local`: The raw local configuration
   - `named`: The raw named configuration (if applicable)

5. **Runtime Context** (if `include_context=True`):
   - The complete runtime context, which is the merged configuration based on precedence rules

6. **CLI Arguments** (if `include_cli_args=True`):
   - `cli_args`: The parsed command-line arguments
   - `sys_argv`: The raw system arguments array

7. **Command Context**:
   - Information about the current command being executed

## The `config status` Command

The `config status` command provides a user-friendly way to access this JSON representation:

```bash
cli-tool config status [OPTIONS]
```

### Options

- `--include-paths/--no-paths`: Include file paths in output (default: include)
- `--include-configs/--no-configs`: Include raw configurations in output (default: include)
- `--include-context/--no-context`: Include runtime context in output (default: include)
- `--include-cli-args/--no-cli-args`: Include CLI arguments in output (default: include)
- `--format [json|table]`: Output format (default: json)

### Examples

1. View complete configuration status in JSON format:
   ```bash
   cli-tool config status
   ```

2. View simplified output in table format:
   ```bash
   cli-tool config status --format table
   ```

3. View only the basic information and configuration status:
   ```bash
   cli-tool config status --no-paths --no-configs --no-context --no-cli-args
   ```

4. Check configuration status with a specific scope:
   ```bash
   cli-tool config status --global
   cli-tool config status --file my-config.json
   ```

## Use Cases

### Debugging Configuration Issues

When configuration isn't being applied as expected, you can use the `config status` command to see exactly what's happening:

```bash
cli-tool config status --verbose
```

This will show you:
- Which configuration files exist and are being loaded
- The current scope that's being used
- The exact content of each configuration file
- The final merged configuration after applying precedence rules

### Understanding Scope Resolution

To understand how scope flags are being processed:

```bash
cli-tool --global config status --include-cli-args
```

This will show you whether the `--global` flag is being properly detected and applied.

### Troubleshooting Command Context

When developing new commands, it can be useful to see how the command context is being built:

```bash
cli-tool config status --include-context --no-configs
```

This will show you the command path, command name, and parent commands that are being detected.

## Implementation Details

### Deep Copying

The method uses deep copies of dictionaries to ensure it doesn't accidentally modify the original data:

```python
# Make a deep copy to avoid modifying the original
import copy
context_copy = copy.deepcopy(self.context)
```

### Selective Output

The method accepts parameters to control which sections are included in the output, allowing users to focus on the information they need:

```python
# Add raw configurations if requested
if include_configs:
    result["configs"] = { ... }
```

### Table Output Format

For the table output format, the implementation flattens the nested structure to make it more readable in a tabular form:

```python
# For table format, flatten and simplify the structure
table_data = []

# Add basic info
table_data.append({"Category": "Basic", "Key": "Current Scope", "Value": status_json.get("current_scope", "unknown")})
```

## Conclusion

The `to_json` method and `config status` command provide powerful tools for inspecting and debugging the configuration system. They offer deep insight into how configuration is loaded, merged, and applied, making it easier to understand and troubleshoot configuration-related issues.

This functionality is particularly valuable during development and debugging, as it allows developers to verify that the configuration system is working as expected and to identify any issues in how configuration values are being resolved.