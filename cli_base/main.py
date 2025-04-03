#!/usr/bin/env python3
"""
Universal CLI template with standardized commands, profiles, and configuration management.
"""

import click
from cli_base.commands.config_cmd import config_group
from cli_base.extensibility.llm_extension import llm_group
from cli_base.commands.schema_cmd import schema_group
from cli_base.commands.advanced_cmd import advanced_command
from cli_base.utils.context import ContextManager
from cli_base.utils.formatting import OutputFormatter

# Import the generate command for LLM interaction
try:
    from cli_base.llm.commands import generate_command
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False


@click.group()
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.option("--global", "scope", flag_value="global", help="Use global configuration")
@click.option("--local", "scope", flag_value="local", is_flag=True, help="Use local configuration")
@click.option("--file", "file_path", type=str, help="Use named configuration file")
def cli(verbose: bool, quiet: bool, scope: str = None, file_path: str = None):
    """
    Universal CLI template with standardized commands, profiles, and configuration management.
    
    Use commands like 'config', 'llm', and 'schema' to interact with the tool.
    """
    # Initialize runtime settings with global CLI arguments
    cli_args = {
        "verbose": verbose,
        "quiet": quiet,
        "scope": scope,
        "file_path": file_path
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
cli.add_command(advanced_command)

# Add LLM generate command if LangChain is available
if HAS_LANGCHAIN:
    cli.add_command(generate_command)
# Add other profile command groups here

# Now register all commands in the CommandRegistry
from cli_base.utils.command_registry import CommandRegistry
registry = CommandRegistry.get_instance()
registry.register_commands_from_cli(cli)

# Import advanced settings system (but don't activate it by default)
from cli_base.utils.advanced_settings import (
    AdvancedRTSettings, 
    AdvancedContextManager,
    initialize_advanced_context,
    get_parameter_value
)
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

def initialize_with_advanced_settings():
    """
    Initialize the CLI with advanced settings instead of regular settings.
    
    This function replaces the standard context manager with the advanced
    context manager, enabling command-specific configurations and enhanced
    parameter resolution for all commands.
    
    Usage:
        # At the beginning of the script:
        if use_advanced_settings:
            initialize_with_advanced_settings()
            
        # Then run the CLI:
        cli()
    """
    # Create a parameter resolver
    resolver = ParameterResolver()
    
    # Create dummy Click context if running outside of Click
    try:
        click.get_current_context()
    except RuntimeError:
        # Create dummy Click context for initialization
        ctx = click.Context(cli)
        ctx.ensure_object(dict)
        with ctx:
            # Initialize advanced context
            advanced_ctx = initialize_advanced_context(resolver=resolver)
            
            # Store reference to make it accessible
            cli.advanced_context = advanced_ctx
    
    # Monkey patch ContextManager to use advanced settings
    def get_instance_with_advanced():
        """Get the advanced context manager instance instead of regular one."""
        try:
            # Try to get existing advanced context manager
            return AdvancedContextManager.get_advanced_instance()
        except RuntimeError:
            # Initialize new advanced context manager
            return AdvancedContextManager.initialize_advanced()
    
    # Replace ContextManager.get_instance with our version
    ContextManager.get_instance = get_instance_with_advanced
    
    # Log that advanced settings are being used
    from cli_base.utils.formatting import OutputFormatter
    OutputFormatter.print_info("Advanced settings system activated.")

if __name__ == "__main__":
    # Check if advanced settings should be enabled
    import os
    use_advanced_settings = os.environ.get("CLI_USE_ADVANCED_SETTINGS", "").lower() in ("1", "true", "yes", "on")
    
    use_advanced_settings = True
    if use_advanced_settings:
        initialize_with_advanced_settings()
    
    cli()