"""
Schema command module.
Provides a visual representation of the command structure.
"""

import click
from ..utils.context import ContextManager
from ..utils.formatting import OutputFormatter
from ..utils.command_registry import CommandRegistry
from .cmd_options import standard_command

@click.group(name="schema")
def schema_group():
    """Display command structure as ASCII art."""
    pass


@standard_command(init_context=False)
@schema_group.command(name="show")
@click.argument("command", required=False)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def show_schema(command: str, verbose: bool, scope: str = None, file_path: str = None):
    """Show schema for a specific command or the entire CLI."""
    # Initialize context with verbose parameter
    ctx = ContextManager.initialize({"scope": scope, "file_path": file_path, "verbose": verbose})
    
    # Get command registry
    registry = CommandRegistry.get_instance()
    
    if command:
        # Show schema for specific command
        if registry.get_command(command):
            command_schema = registry.get_schema(command)
            OutputFormatter.print_command_tree(command_schema)
        else:
            # Command not found
            OutputFormatter.print_error(f"Command not found: {command}")
    else:
        # Show schema for all commands
        schema_data = registry.get_schema()
        OutputFormatter.print_command_tree(schema_data)