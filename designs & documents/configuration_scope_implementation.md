# Configuration Scope Implementation Guide

This document describes the implementation details of the configuration scope options (`--global`, `--local`, and `--file`) that can be used with any command in the CLI tool.

## Implementation Overview

The configuration scope options have been implemented to work uniformly across all commands. This required several key changes to the codebase:

1. Creating a `scope_options` decorator for individual commands
2. Developing a `standard_command` decorator that combines common patterns
3. Adding robust CLI argument detection for scope options
4. Modifying the context initialization mechanism to process these options
5. Updating the runtime configuration loading logic to respect scope precedence rules
6. Enhancing profile management to look for profiles across all configuration scopes

## Key Components

### 1. Scope Options Decorator

A dedicated `scope_options` decorator has been added to `cmd_options.py` that can be applied to any command:

```python
SCOPE_PARAMS = [
    # The order is important - the global option needs to be first to take precedence
    {"name": "global", "func_param":"scope", "flag_value": "global", "help": "Use global configuration"},
    {"name": "local", "func_param":"scope", "flag_value": "local", "default": True, "help": "Use local configuration"},
    {"name": "file", "func_param":"file_path", "type": str, "help": "Use named configuration file"},
]

def scope_options(command):
    """Decorator to add scope options to a command."""
    for param in SCOPE_PARAMS:
        command = click.option(
            f"--{param['name']}", 
            param['func_param'],
            flag_value=param.get('flag_value', None) if 'flag_value' in param else None,
            type=param['type'] if 'type' in param else None, 
            default=param.get('default', None) if 'default' in param else None,
            help=param['help']
        )(command)
    return command
```

### 2. Standard Command Decorator

The `standard_command` decorator combines several common patterns:

```python
def standard_command(init_context: bool = True) -> Callable[[CommandFunc], CommandFunc]:
    """
    Comprehensive decorator for standard command patterns.
    
    This decorator combines several common patterns for CLI commands:
    1. Adds configuration scope options (--global, --local, --file)
    2. Initializes the context with scope parameters (optional)
    3. Resolves parameters via the parameter resolver
    """
    def decorator(func: CommandFunc) -> CommandFunc:
        # Apply scope options
        func = scope_options(func)
        
        # Create a wrapper that initializes context
        @functools.wraps(func)
        def context_wrapper(*args, **kwargs):
            # Extract scope parameters
            scope_params = {
                "scope": kwargs.get("scope"),
                "file_path": kwargs.get("file_path")
            }
            
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
            
            # Initialize context if requested
            if init_context:
                try:
                    initialize_context(scope_params)
                except Exception as e:
                    from ..utils.formatting import OutputFormatter
                    OutputFormatter.print_error(f"Error initializing context: {str(e)}")
            
            # Call the original function
            return func(*args, **kwargs)
        
        # Return either the context wrapper or the param resolver + context wrapper
        if init_context:
            # Apply context initialization before parameter resolution
            return with_resolved_params(context_wrapper)
        else:
            # Just apply parameter resolution
            return with_resolved_params(func)
    
    return decorator
```

### 3. Context Initialization

The `initialize_context` function in `context.py` initializes or updates an existing context:

```python
def initialize_context(cli_args: Optional[Dict[str, Any]] = None,
                       resolver: Optional['ParameterResolver'] = None) -> ContextManager:
    """
    Initialize or update the context manager with advanced settings.
    
    This function serves as the main entry point for initializing
    the context manager.
    """
    # Make sure cli_args is at least an empty dict if None
    if cli_args is None:
        cli_args = {}
    
    try:
        # Try to get existing context manager
        ctx = ContextManager.get_instance()
        
        # Update with new args if provided
        if cli_args:
            from .advanced_settings import AdvancedRTSettings
            ctx._settings = AdvancedRTSettings(cli_args, resolver)
        
        return ctx
    except RuntimeError:
        # No context manager exists, initialize one
        try:
            return ContextManager.initialize(cli_args, resolver)
        except Exception as e:
            # In case of error during initialization, provide fallback behavior
            from .formatting import OutputFormatter
            OutputFormatter.print_error(f"Warning: Error initializing context: {str(e)}")
            
            # Create a basic instance
            from .advanced_settings import AdvancedRTSettings
            instance = ContextManager()
            instance._settings = AdvancedRTSettings(cli_args, resolver)
            ContextManager._instance = instance
            return instance
```

### 4. Improved Scope Detection

The `_build_runtime_context` method in `AdvancedRTSettings` class has been updated to better detect and handle configuration scopes:

```python
def _build_runtime_context(self):
    """
    Build the runtime context by merging configurations according to precedence rules
    based on which configuration scope options are specified.
    """
    # Start with defaults
    runtime_config = self.DEFAULT_CONFIG.copy()
    
    # Determine current scope by checking system arguments directly
    # This is more reliable than checking the resolved parameters
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
    
    # Also check if scope and file parameters are set through other means
    current_scope = self.cli_args.get("scope", "local")
    if current_scope == "global":
        use_global = True
        
    cli_file_path = self.cli_args.get("file_path")
    if cli_file_path:
        use_file = True
        file_path = cli_file_path
    
    # Build config according to specified scope
    # (Implementation follows precedence rules)
```

## Using Standard Command in Your Commands

To use the `standard_command` decorator with a command:

```python
@standard_command()
@config_group.command("show")
def show_config(scope: Optional[str] = None, file_path: Optional[str] = None):
    """Display configuration content."""
    # Context is already initialized by standard_command
    ctx = ContextManager.get_instance()
    rt = ctx.settings
    
    # Validate scope + file_path combination
    if scope is None and file_path is None:
        scope = "local"  # Default to local if not specified
    
    # Command implementation...
```

Important points about the decorator order:

1. `@standard_command()` must be applied first (outermost)
2. Then the Click command decorator (`@config_group.command("show")`)
3. Then any Click option or argument decorators

## Enhanced Profile Management

The LLM profile management system uses the context's configuration scope to locate profiles:

```python
# Get the profile based on name and current scope
try:
    profile_data = profile_manager.get_profile(profile)
except ValueError:
    OutputFormatter.print_error(f"Profile '{profile}' not found.")
    
    # Show available profiles from all scopes
    for scope in ["global", "local"]:
        try:
            profiles = profile_manager.list_profiles(scope)
            if profiles:
                OutputFormatter.print_info(f"  {scope} profiles: {', '.join(profiles.keys())}")
        except Exception:
            pass
```

## Special Auto-Detection for Scope Options

To ensure scope options are correctly detected even when they're specified on the root command, the system now checks:

1. The resolved parameter values first
2. Directly examines `sys.argv` as a fallback
3. Uses fallback behavior if neither detection method works

This approach ensures that a command like:
```
cli-tool --global generate prompt "Why is the sky blue?"
```

Will properly use the global configuration scope, even though the `--global` flag is specified at the root command level rather than on the subcommand.

## Conclusion

This implementation provides a consistent way to specify which configuration scope to use with any command in the CLI tool. Users can now use `--global`, `--local`, and `--file` options with any command, making the tool much more flexible and user-friendly.

The enhanced scope detection ensures reliable behavior regardless of where in the command the scope option appears. The `standard_command` decorator vastly simplifies command implementation while ensuring consistent behavior across all commands.

For more information on how to use the `standard_command` decorator, see the `standard_command_decorator.md` document.