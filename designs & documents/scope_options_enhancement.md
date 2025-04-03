# Scope Options Enhancement

This document outlines the recent enhancements to the configuration scope options system to fix several issues and improve reliability.

## Issues Addressed

The implementation of configuration scope options (`--global`, `--local`, and `--file`) had the following issues:

1. **Global Flag Not Recognized**: When using the `--global` flag, the system would still default to using the local configuration.
2. **File Path Not Respected**: When specifying a file path with `--file`, the system sometimes wouldn't use the specified configuration file.
3. **Decorator Order Issues**: The order of decorators affected whether scope options were properly applied.
4. **Inconsistent Behavior**: Different commands handled scope options differently.

## Implemented Solutions

### 1. More Robust Scope Option Detection

Enhanced scope detection by checking multiple sources:

```python
# Determine current scope by checking system arguments directly
sys_argv = self.cli_args.get('sys.argv', [])
sys_argv_str = ' '.join(sys_argv)

# Check for global flag
use_global = False
if '--global' in sys_argv_str:
    use_global = True

# Check for file flag
use_file = False
file_path = None
if '--file' in sys_argv_str:
    use_file = True
    try:
        file_index = sys_argv.index('--file')
        if file_index + 1 < len(sys_argv):
            file_path = sys_argv[file_index + 1]
    except (ValueError, IndexError):
        pass
```

### 2. Direct Command-Line Argument Access

Added direct access to command-line arguments within the standard_command decorator:

```python
# Handle global flag and file path specially
import sys
if "--global" in sys.argv:
    scope_params["scope"] = "global"
    
# Check for file parameter
if "--file" in sys.argv:
    try:
        file_index = sys.argv.index("--file")
        if file_index + 1 < len(sys.argv):
            scope_params["file_path"] = sys.argv[file_index + 1]
    except ValueError:
        pass
```

### 3. Corrected Decorator Order

Ensured the correct ordering of decorators for all commands:

```python
# CORRECT ORDER - standard_command must be first (outermost)
@standard_command()
@config_group.command("show")
@click.option("--some-option", help="Some option")
def show_config(...):
    """Command docs"""
    # ...
```

### 4. Improved Error Handling

Enhanced error handling and diagnostics when loading configuration files:

```python
# If we have a file path but the named_config wasn't loaded, try loading it again
if has_file_option and file_path and not self.named_config:
    self.named_config_path = Path(os.path.expanduser(file_path))
    if self.named_config_path.exists():
        try:
            with open(self.named_config_path, 'r') as f:
                self.named_config = json.load(f)
            if self.verbose:
                OutputFormatter.print_info(f"Loaded named config from {file_path}")
        except (json.JSONDecodeError, IOError) as e:
            if self.verbose:
                OutputFormatter.print_error(f"Error loading named config: {str(e)}")
```

### 5. Auto-Initialization of Context Manager

Modified the ContextManager to auto-initialize if needed:

```python
@classmethod
def get_instance(cls) -> 'ContextManager':
    if cls._instance is None:
        # Auto-initialize with default settings rather than raising an error
        return cls.initialize({"scope": "local"})
    return cls._instance
```

### 6. Better Command-Line Args Tracking

Added system arguments to CLI args for better flag checking:

```python
# Add system arguments to CLI args for better flag checking
import sys
self.cli_args["sys.argv"] = sys.argv
```

## Benefits of the Enhancements

1. **Consistent Behavior**: Configuration scope options now work consistently across all commands
2. **Greater Reliability**: Multiple detection mechanisms ensure scope options are properly recognized
3. **Improved User Experience**: Helpful error messages and graceful fallback behavior
4. **Simplified Command Implementation**: The `standard_command` decorator makes it easy to implement new commands with proper scope handling

## Usage Examples

The enhanced scope options now work correctly in all the following scenarios:

```bash
# Global flag at root level
cli-tool --global generate prompt "Why is the sky blue?"

# Global flag at command level
cli-tool generate prompt "Why is the sky blue?" --global

# File flag with path
cli-tool generate prompt "Why is the sky blue?" --file .working-global.json

# Multiple commands with the same scope
cli-tool --global config show
cli-tool --global llm list
cli-tool --global generate prompt "Sample prompt"
```

## Conclusion

These enhancements have significantly improved the reliability and consistency of the configuration scope options. Users can now confidently use `--global`, `--local`, and `--file` options with any command, knowing that the specified configuration scope will be properly respected.

The `standard_command` decorator further simplifies command implementation while ensuring consistent handling of scope options across all commands.