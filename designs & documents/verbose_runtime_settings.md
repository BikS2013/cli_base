# Verbose Runtime Settings Output

This document explains the implementation of displaying runtime settings JSON when verbose output is enabled.

## Overview

The CLI tool now displays a complete JSON representation of the runtime settings when verbose output is enabled using the `-v` or `--verbose` flag. This provides a detailed view of the current configuration state, command context, and other runtime information, which is particularly useful for debugging and development.

## Implementation

The implementation includes the following components:

1. The `to_json` method in the `AdvancedRTSettings` class
2. A verbose mode flag in the `OutputFormatter` class
3. Runtime settings output in the `standard_command` decorator

### The `to_json` Method

The `AdvancedRTSettings` class now includes a `to_json` method that produces a comprehensive JSON representation of the runtime state:

```python
def to_json(self, include_paths: bool = True, include_configs: bool = True, 
           include_context: bool = True, include_cli_args: bool = True) -> Dict[str, Any]:
    """
    Produce a complete JSON representation of the current state.
    """
    # Implementation details...
```

This method generates a structured JSON object that includes:

- Basic settings information
- File paths and configuration status
- Raw configurations (optional)
- Runtime context and command information
- CLI arguments and system arguments

### Verbose Mode in OutputFormatter

The `OutputFormatter` class now has a class variable to track verbose mode and methods to control it:

```python
class OutputFormatter:
    # Class variable to track verbose mode
    verbose_mode = False
    
    @classmethod
    def set_verbose(cls, verbose: bool):
        """Set verbose mode for the output formatter."""
        cls.verbose_mode = verbose
```

The main CLI entry point sets this flag based on the `--verbose` command-line option:

```python
@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def cli(verbose: bool, ...):
    # Set verbose mode in OutputFormatter
    from cli_base.utils.formatting import OutputFormatter
    OutputFormatter.set_verbose(verbose)
```

### Printing Runtime Settings

The `OutputFormatter` class now includes a method to print the runtime settings:

```python
@classmethod
def print_runtime_settings(cls, include_configs: bool = False):
    """
    Print the runtime settings JSON representation when in verbose mode.
    """
    if not cls.verbose_mode:
        return
        
    try:
        # Get the context and settings
        ctx = ContextManager.get_instance()
        rt = ctx.settings
        
        # Generate a JSON representation of the settings
        status_json = rt.to_json(...)
        
        # Print the JSON with a title
        cls.print_json(status_json, "Runtime Settings (Verbose Mode)")
    except Exception as e:
        cls.print_warning(f"Could not display runtime settings: {str(e)}")
```

### Standard Command Decorator Integration

The `standard_command` decorator has been updated to print runtime settings after command execution when verbose mode is enabled:

```python
try:
    # Call the original function and get the result
    result = func(*args, **kwargs)
    
    # If verbose mode is enabled, display runtime settings after command execution
    from ..utils.formatting import OutputFormatter
    OutputFormatter.print_runtime_settings(include_configs=False)
    
    return result
except Exception as e:
    # If there's an error, still try to display runtime settings if in verbose mode
    from ..utils.formatting import OutputFormatter
    OutputFormatter.print_runtime_settings(include_configs=False)
    
    # Re-raise the exception
    raise e
```

This ensures that runtime settings are displayed after any command that uses the `standard_command` decorator, providing consistent behavior across the CLI tool.

## Usage

To enable verbose output and see the runtime settings, use the `-v` or `--verbose` flag with any command:

```bash
cli-tool -v config show
cli-tool --verbose generate prompt "Hello, world!"
cli-tool -v llm list
```

The verbose output includes:

1. The original command output
2. Followed by a JSON representation of the runtime settings, showing:
   - Current configuration scope
   - Configuration file paths and existence status
   - Command context
   - System arguments and parsed CLI arguments
   - Other runtime information

## Benefits

This implementation provides several benefits:

1. **Debugging**: Easily see what configuration is being used and where values are coming from
2. **Development**: Understand how the CLI tool's components interact
3. **Support**: Help users troubleshoot issues by seeing the complete runtime state
4. **Transparency**: Make it clear how configuration values are being resolved

The verbose output is only displayed when explicitly requested, so it doesn't clutter normal operations, but is readily available when needed.