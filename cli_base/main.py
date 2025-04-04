#!/usr/bin/env python3
"""
Universal CLI template with standardized commands, profiles, and configuration management.
"""

import click
from cli_base.commands.config_cmd import config_group
from cli_base.extensibility.llm_extension import llm_group
from cli_base.commands.schema_cmd import schema_group
from cli_base.commands.advanced_cmd import advanced_command
from cli_base.commands.cmd_options import scope_options, standard_command
from cli_base.utils.context import ContextManager
from cli_base.utils.formatting import OutputFormatter

# Import the LLM commands
try:
    from cli_base.llm.commands import ask_command, chat_command
    from cli_base.extensibility.clipboard_extension import get_clipboard_command
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False


@click.group()
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@scope_options
def cli(verbose: bool, quiet: bool, scope: str = None, file_path: str = None):
    """
    Universal CLI template with standardized commands, profiles, and configuration management.
    
    Use commands like 'config', 'llm', and 'schema' to interact with the tool.
    """
    # Set verbose mode in OutputFormatter
    from cli_base.utils.formatting import OutputFormatter
    OutputFormatter.set_verbose(verbose)
    
    # If verbose mode is enabled, display the runtime settings
    # (This will happen after command execution - we'll add explicit calls in each command)


# Add command groups
cli.add_command(config_group)
cli.add_command(llm_group)
cli.add_command(schema_group)
cli.add_command(advanced_command)

# Add LLM commands if LangChain is available
if HAS_LANGCHAIN:
    cli.add_command(ask_command)          # 'ask' command for one-off queries
    cli.add_command(chat_command)         # 'chat' command for interactive sessions
    cli.add_command(get_clipboard_command)  # 'get-clipboard' command to convert clipboard content
# Add other profile command groups here

# Now register all commands in the CommandRegistry
from cli_base.utils.command_registry import CommandRegistry
registry = CommandRegistry.get_instance()
registry.register_commands_from_cli(cli)

# Import settings system
from cli_base.utils.advanced_settings import get_parameter_value
from cli_base.utils.context import initialize_context
from cli_base.utils.param_resolver import ParameterResolver


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

def initialize_settings():
    """
    Initialize the CLI with settings.
    
    This function initializes the context manager with settings,
    enabling command-specific configurations and parameter resolution.
    """
    # Create a parameter resolver
    resolver = ParameterResolver()
    
    # Initialize with default settings first to ensure we have a base configuration
    scope_params = {"scope": "local"}  # Default to local scope
    
    # Check for verbose flag in sys.argv
    import sys
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    
    # Set verbose mode in OutputFormatter
    from cli_base.utils.formatting import OutputFormatter
    OutputFormatter.set_verbose(verbose)
    
    # Initialize context
    ctx = initialize_context(scope_params, resolver=resolver)
    
    # Store reference to make it accessible
    cli.context = ctx
    
    # Log that settings are being used
    OutputFormatter.print_info("Settings system activated.")

if __name__ == "__main__":
    # Always initialize settings
    initialize_settings()
    
    # Run the CLI
    cli()