#!/usr/bin/env python3
"""
Universal CLI template with standardized commands, profiles, and configuration management.
"""

import click
from cli_base.commands.config_cmd import config_group
from cli_base.extensibility.llm_extension import llm_group
from cli_base.commands.schema_cmd import schema_group
from cli_base.utils.context import ContextManager
from cli_base.utils.formatting import OutputFormatter


@click.group()
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
def cli(verbose: bool, quiet: bool):
    """
    Universal CLI template with standardized commands, profiles, and configuration management.
    
    Use commands like 'config', 'llm', and 'schema' to interact with the tool.
    """
    # Initialize runtime settings with global CLI arguments
    cli_args = {
        "verbose": verbose,
        "quiet": quiet
    }
    
    try:
        # Try to get existing context manager instance
        ctx = ContextManager.get_instance()
    except RuntimeError:
        # Initialize new context manager
        ctx = ContextManager.initialize(cli_args)


# Add command groups
cli.add_command(config_group)
cli.add_command(llm_group)
cli.add_command(schema_group)
# Add other profile command groups here

# Now register all commands in the CommandRegistry
from cli_base.utils.command_registry import CommandRegistry
registry = CommandRegistry.get_instance()
registry.register_commands_from_cli(cli)


@cli.command(name="help")
@click.argument("command", required=False)
@click.argument("subcommand", required=False)
def help_command(command, subcommand):
    """Display help information for commands."""
    ctx = click.get_current_context()
    
    # Get command registry
    from cli_base.utils.command_registry import CommandRegistry
    registry = CommandRegistry.get_instance()
    
    if command:
        # Show help for a specific command
        cmd_obj = registry.get_command(command)
        
        if cmd_obj:
            if subcommand and subcommand in cmd_obj.commands:
                # Show help for a specific subcommand
                sub_cmd = cmd_obj.commands[subcommand]
                click.echo(sub_cmd.get_help(ctx))
            else:
                # Show help for the command
                click.echo(cmd_obj.get_help(ctx))
        else:
            OutputFormatter.print_error(f"Unknown command: {command}")
    else:
        # Show general help
        click.echo(ctx.parent.get_help())

if __name__ == "__main__":
    cli()