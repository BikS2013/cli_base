#!/usr/bin/env python3
"""
Universal CLI template with standardized commands, profiles, and configuration management.
"""

import click
from cli_base.commands.config_cmd import config_group
from cli_base.commands.llm_cmd import llm_group
from cli_base.commands.schema_cmd import schema_group
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
    # Store global options in click context
    ctx = click.get_current_context()
    ctx.obj = {
        "verbose": verbose,
        "quiet": quiet
    }


# Add command groups
cli.add_command(config_group)
cli.add_command(llm_group)
cli.add_command(schema_group)


@cli.command(name="help")
@click.argument("command", required=False)
@click.argument("subcommand", required=False)
def help_command(command, subcommand):
    """Display help information for commands."""
    ctx = click.get_current_context()
    
    if command:
        # Show help for a specific command
        if command in ctx.parent.command.commands:
            cmd = ctx.parent.command.commands[command]
            
            if subcommand and subcommand in cmd.commands:
                # Show help for a specific subcommand
                sub_cmd = cmd.commands[subcommand]
                click.echo(sub_cmd.get_help(ctx))
            else:
                # Show help for the command
                click.echo(cmd.get_help(ctx))
        else:
            OutputFormatter.print_error(f"Unknown command: {command}")
    else:
        # Show general help
        click.echo(ctx.parent.get_help())


if __name__ == "__main__":
    cli()