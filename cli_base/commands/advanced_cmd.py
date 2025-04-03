"""
Advanced command example showing usage of AdvancedRTSettings.
Demonstrates how to use the advanced parameter resolution system.
"""

import click
from typing import Optional, Dict, Any

from cli_base.utils.advanced_settings import (
    AdvancedRTSettings, 
    initialize_advanced_context, 
    get_parameter_value
)
from cli_base.utils.formatting import OutputFormatter
from cli_base.commands.cmd_options import global_scope_options


@click.group("advanced")
def advanced_group():
    """Command group demonstrating advanced parameter resolution."""
    pass


@advanced_group.command("config")
@click.argument("key", required=False)
@click.argument("value", required=False)
@global_scope_options
def advanced_config(key: Optional[str] = None, value: Optional[str] = None, 
                   scope: Optional[str] = None, file_path: Optional[str] = None):
    """
    View or set command-specific configuration.
    
    If no arguments are provided, shows all command-specific configurations.
    If only KEY is provided, shows the value for that key.
    If both KEY and VALUE are provided, sets the value for that key.
    """
    # Initialize advanced context
    ctx = initialize_advanced_context({
        "scope": scope,
        "file_path": file_path
    })
    advanced_settings = ctx.advanced_settings
    
    # Get current command path
    command_path = advanced_settings.command_context.get("command_path")
    if not command_path:
        OutputFormatter.print_error("Unable to determine command path.")
        return
    
    # Handle viewing configurations
    if key is None:
        # Show all command configurations
        all_commands = {}
        
        # Get command configs from all scopes
        for scope_name in ["global", "local"]:
            try:
                config = advanced_settings.get_config(scope_name)
                if "commands" in config:
                    for cmd_path, cmd_config in config["commands"].items():
                        if cmd_path not in all_commands:
                            all_commands[cmd_path] = {}
                        all_commands[cmd_path][scope_name] = cmd_config
            except ValueError:
                pass
            
        # Show combined results
        if not all_commands:
            OutputFormatter.print_info("No command-specific configurations found.")
        else:
            OutputFormatter.print_info("Command-specific configurations:")
            for cmd_path, scopes in all_commands.items():
                OutputFormatter.print_info(f"\n[bold]{cmd_path}[/bold]:")
                for scope_name, config in scopes.items():
                    OutputFormatter.print_info(f"  {scope_name}: {config}")
    
    # Handle viewing specific key
    elif value is None:
        # Show value for specific key
        cmd_config = advanced_settings.get_command_config(command_path)
        if key in cmd_config:
            OutputFormatter.print_info(f"{key} = {cmd_config[key]} (from command config)")
        else:
            param_value = get_parameter_value(key)
            if param_value is not None:
                OutputFormatter.print_info(f"{key} = {param_value} (from general settings)")
            else:
                OutputFormatter.print_info(f"No configuration found for key: {key}")
    
    # Handle setting specific key
    else:
        # Convert value to appropriate type
        typed_value = value
        if value.lower() == "true":
            typed_value = True
        elif value.lower() == "false":
            typed_value = False
        elif value.isdigit():
            typed_value = int(value)
        elif all(c.isdigit() or c == '.' for c in value) and value.count('.') == 1:
            typed_value = float(value)
        
        # Set value for specific key
        current_scope = advanced_settings.context.get("current_scope", "local")
        updates = {key: typed_value}
        advanced_settings.update_command_config(command_path, updates, current_scope)
        OutputFormatter.print_info(f"Set {key} = {typed_value} for command {command_path} in {current_scope} configuration.")


@advanced_group.command("exec")
@click.argument("command_name")
@click.option("--param1", help="Example parameter 1")
@click.option("--param2", help="Example parameter 2")
@click.option("--param3", type=int, help="Example parameter 3")
@global_scope_options
def advanced_exec(command_name: str, param1: Optional[str] = None, 
                 param2: Optional[str] = None, param3: Optional[int] = None,
                 scope: Optional[str] = None, file_path: Optional[str] = None):
    """
    Execute a command with resolved parameters.
    
    This command demonstrates how parameters are resolved from different sources.
    """
    # Initialize advanced context
    ctx = initialize_advanced_context({
        "scope": scope,
        "file_path": file_path,
        "param1": param1,
        "param2": param2,
        "param3": param3
    })
    advanced_settings = ctx.advanced_settings
    
    # Get parameters using advanced parameter resolution
    resolved_param1 = get_parameter_value("param1", "default1")
    resolved_param2 = get_parameter_value("param2", "default2")
    resolved_param3 = get_parameter_value("param3", 0)
    
    # Execute the command (simulated)
    OutputFormatter.print_info(f"Executing command: {command_name}")
    OutputFormatter.print_info("Resolved parameters:")
    OutputFormatter.print_info(f"  param1 = {resolved_param1}")
    OutputFormatter.print_info(f"  param2 = {resolved_param2}")
    OutputFormatter.print_info(f"  param3 = {resolved_param3}")
    
    # Show parameter sources
    OutputFormatter.print_info("\nParameter sources:")
    for param_name, param_value in [
        ("param1", resolved_param1),
        ("param2", resolved_param2),
        ("param3", resolved_param3)
    ]:
        source = "Default"
        
        if param_name in advanced_settings.cli_args and advanced_settings.cli_args[param_name] is not None:
            source = "Command-line argument"
        else:
            cmd_config = advanced_settings.get_command_config()
            if param_name in cmd_config:
                source = f"Command configuration ({advanced_settings.context.get('current_scope', 'unknown')})"
            elif param_name in advanced_settings.context["settings"]:
                source = "General settings"
        
        OutputFormatter.print_info(f"  {param_name}: {source}")


# Export the command group
advanced_command = advanced_group