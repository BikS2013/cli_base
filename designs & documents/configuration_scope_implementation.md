# Configuration Scope Implementation Guide

This document describes the implementation details of the configuration scope options (`--global`, `--local`, and `--file`) that can be used with any command in the CLI tool.

## Implementation Overview

The configuration scope options have been implemented to work uniformly across all commands. This required several key changes to the codebase:

1. Adding the scope options to the main CLI entry point
2. Creating a global_scope_options decorator for individual commands
3. Modifying the context initialization mechanism to process these options
4. Updating the runtime configuration loading logic to respect scope precedence rules
5. Enhancing profile management to look for profiles across all configuration scopes

## Key Components

### 1. Global Scope Options Decorator

A new decorator `global_scope_options` has been added to `cmd_options.py` that can be applied to any command:

```python
def global_scope_options(command):
    """
    Decorator to add scope options (--global, --local, --file) to any command.
    This decorator is used to ensure consistent configuration handling across all commands.
    """
    for param in SCOPE_PARAMS:
        command = click.option(
            f"--{param['name']}", 
            param['func_param'],
            flag_value=param.get('flag_value', None) if 'flag_value' in param else None,
            type=param['type'] if 'type' in param else None, 
            default=param.get('default', None) if 'default' in param else None,
            help=param['help'],
            is_eager=True,  # Process these options before other options
            expose_value=True,  # Make sure values are passed to the function
        )(command)
    return command
```

The `is_eager=True` flag ensures these options are processed early, so they can affect the configuration loading.

### 2. Main CLI Modifications

The main CLI function now includes the scope options directly:

```python
@click.group()
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.option("--global", "scope", flag_value="global", help="Use global configuration")
@click.option("--local", "scope", flag_value="local", is_flag=True, help="Use local configuration")
@click.option("--file", "file_path", type=str, help="Use named configuration file")
def cli(verbose: bool, quiet: bool, scope: str = None, file_path: str = None):
    # Command implementation...
```

This allows the scope options to be used with any command, as they're captured at the top level.

### 3. Context Initialization

The `_initialize_context` function in `context.py` has been enhanced to update an existing context with new CLI arguments:

```python
def _initialize_context(cli_args: Dict[str, Any]) -> ContextManager:
    """
    Initialize or get the context manager instance.
    
    This function checks if the context manager has already been initialized.
    If it has, it will update the context with any new CLI arguments,
    particularly focusing on configuration scope options (--global, --local, --file).
    """
    try:
        # Get existing context manager
        ctx = ContextManager.get_instance()
        
        # Update existing context with configuration scope options if provided
        if cli_args:
            current_settings = ctx.settings
            
            # Update file_path option if provided
            if cli_args.get("file_path"):
                current_settings.cli_args["file_path"] = cli_args["file_path"]
                current_settings.named_config_path = None  # Reset to force reload
                current_settings.named_config = None
            
            # Update scope option if provided
            if cli_args.get("scope"):
                current_settings.cli_args["scope"] = cli_args["scope"]
                current_settings.context["current_scope"] = cli_args["scope"]
            
            # Reload configurations and rebuild context with updated settings
            current_settings._load_configurations()
            current_settings._build_runtime_context()
        
        return ctx
    except RuntimeError:
        # Initialize new context manager if not already initialized
        return ContextManager.initialize(cli_args)
```

### 4. Configuration Loading Logic

The `_build_runtime_context` method in `RTSettings` class has been updated to respect configuration scope precedence rules:

```python
def _build_runtime_context(self):
    """
    Build the runtime context by merging configurations according to precedence rules
    based on which configuration scope options are specified.
    
    If --file option is used:
        1. Command line arguments
        2. Named configuration file
        3. Local configuration (for missing elements)
        4. Global configuration (for missing elements)
        5. Default values
        
    If --local option is used:
        1. Command line arguments
        2. Local configuration
        3. Global configuration (for missing elements)
        4. Default values
        
    If --global option is used:
        1. Command line arguments
        2. Global configuration
        3. Default values
    """
    # Implementation details...
```

## Using Configuration Scope Options in Commands

To add scope options to a command, use the `global_scope_options` decorator:

```python
@some_command_group.command("subcommand")
@click.argument("arg1", type=str)
@click.option("--some-option", help="Some option description")
@global_scope_options  # Add this decorator to enable scope options
def my_command_function(arg1, some_option, scope=None, file_path=None):
    """Command documentation"""
    # Initialize context with current cli arguments
    _initialize_context({
        "scope": scope,
        "file_path": file_path
    })
    
    # Command implementation...
```

## Enhanced Profile Management

The profile management system has been enhanced to support cross-scope profile lookups:

### Finding Profiles Across Scopes

New methods were added to the `RTSettings` class:

```python
def get_profile_from_any_scope(self, profile_type: str, name: str) -> Dict[str, Any]:
    """
    Get a specific profile from any available scope, following precedence rules.
    
    This method will first check the current scope, then fall back to
    local, then global configurations looking for a profile with the given name.
    """
    # Implementation follows precedence rules:
    # 1. Check effective config
    # 2. For --file option, check local config
    # 3. Finally check global config
```

### Default Profile Resolution

The default profile resolution was also enhanced to look across all scopes:

```python
def get_default_profile_from_any_scope(self, profile_type: str) -> Optional[str]:
    """
    Get the name of the default profile from any scope, following the precedence rules.
    
    This method will first check the current scope, then fall back to local,
    then global configurations looking for a default profile of the given type.
    """
    # Implementation follows precedence rules as above
```

### Improved Error Handling

The LLM commands were updated to provide more helpful error messages when profiles can't be found, showing which profiles are available in each scope:

```python
# List profiles from all scopes
config_scopes = ["global", "local"]
current_scope = ContextManager.get_instance().settings.context.get("current_scope")
if current_scope == "file":
    config_scopes.append("file")
    
# Show profiles from each scope
for scope in config_scopes:
    try:
        profiles = profile_manager.list_profiles(scope)
        if profiles:
            OutputFormatter.print_info(f"  {scope} profiles: {', '.join(profiles.keys())}")
    except Exception:
        pass
```

## Conclusion

This implementation provides a consistent way to specify which configuration scope to use with any command in the CLI tool. Users can now use `--global`, `--local`, and `--file` options with any command, making the tool much more flexible and user-friendly.

The enhanced profile management system ensures that profiles created in any scope (global, local, or custom file) can be accessed by commands according to the precedence rules, without requiring duplication of profiles across different configuration files.

For further information on how these options work from a user perspective, see the `configuration_scope_options.md` document.