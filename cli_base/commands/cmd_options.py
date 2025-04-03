import click
import functools
from typing import Callable, TypeVar, Optional, Dict, Any, List, Union

# Import these here to avoid circular imports
from ..utils.param_resolver import with_resolved_params
from ..utils.context import initialize_context, ContextManager

# Type variable for command function
CommandFunc = TypeVar('CommandFunc', bound=Callable)

#@click.option("--name", type=str, required=True, help="Profile name")
def profile_name_option(command):
    """Decorator to add profile name option to a command."""
    command = click.option(
        f"--name", 
        type=str,
        required=True,
        help="Profile name"
    )(command)
    return command


SCOPE_PARAMS = [
    # The order is important - the global option needs to be first to take precedence
    {"name": "global", "func_param":"scope", "flag_value": "global", "help": "Use global configuration"},
    {"name": "local", "func_param":"scope", "flag_value": "local", "default": True, "help": "Use local configuration"},
    {"name": "file", "func_param":"file_path", "type": str, "help": "Use named configuration file"},
]

# @click.option("--global", "scope", flag_value="global", help="Use global configuration.")
# @click.option("--local", "scope", flag_value="local", default=True, help="Use local configuration.")
# @click.option("--file", "file_path", type=str, help="Use named configuration file.")

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


#@click.argument("json_input", required=False)
def json_input_argument(command):
    """Decorator to add json input option to a command."""
    command = click.argument(
        "json_input",
        required=False
    )(command)
    return command

#@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="table", help="Output format")

def table_format_option(command):
    """Decorator to add format option to a command."""
    command = click.option(
        f"--format", 
        "output_format",
        type=click.Choice(["json", "table"]),
        default="table",
        help="Output format"
    )(command)
    return command

def json_format_option(command):
    """Decorator to add format option to a command."""
    command = click.option(
        f"--format", 
        "output_format",
        type=click.Choice(["json", "table"]),
        default="table",
        help="Output format"
    )(command)
    return command


def standard_command(init_context: bool = True) -> Callable[[CommandFunc], CommandFunc]:
    """
    Comprehensive decorator for standard command patterns.
    
    This decorator combines several common patterns for CLI commands:
    1. Adds configuration scope options (--global, --local, --file)
    2. Initializes the context with scope parameters (optional)
    3. Resolves parameters via the parameter resolver
    
    Args:
        init_context: Whether to automatically initialize the context
                      Set to False if you want to defer context initialization
                      
    Example usage:
    
    @standard_command()
    @config_group.command("show")
    def show_config(scope: Optional[str] = None, file_path: Optional[str] = None):
        # Context is already initialized, settings already available
        ctx = ContextManager.get_instance()
        rt = ctx.settings
        # Rest of your command implementation...
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
            
            # Handle global flag and file path specially because of decorator ordering issues
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
            
            # Debug information if verbose
            if kwargs.get("verbose", False):
                from ..utils.formatting import OutputFormatter
                OutputFormatter.print_info(f"Decorator received scope: {scope_params}")
                OutputFormatter.print_info(f"All kwargs: {kwargs}")
            
            # Initialize context if requested
            if init_context:
                try:
                    initialize_context(scope_params)
                except Exception as e:
                    from ..utils.formatting import OutputFormatter
                    OutputFormatter.print_error(f"Error initializing context: {str(e)}")
            
            # Call the original function and return the result
            # (Runtime settings will be printed by the command if verbose mode is enabled)
            return func(*args, **kwargs)
        
        # Return either the context wrapper or the param resolver + context wrapper
        if init_context:
            # Apply context initialization before parameter resolution
            return with_resolved_params(context_wrapper)
        else:
            # Just apply parameter resolution
            return with_resolved_params(func)
    
    return decorator
