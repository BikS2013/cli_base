"""
Schema command module.
Provides a visual representation of the command structure.
"""

import click
from ..utils.context import ContextManager
from ..utils.formatting import OutputFormatter
from ..utils.command_registry import CommandRegistry


# # Schema data for the entire CLI
# SCHEMA_DATA = {
#     "config": {
#         "help": "Manage configuration files",
#         "subcommands": {
#             "show": {"help": "Display configuration content", "options": {}},
#             "save": {"help": "Save parameters to configuration", "options": {}},
#             "update": {"help": "Update configuration with parameters", "options": {}},
#             "replace": {"help": "Replace entire configuration", "options": {}},
#             "import": {"help": "Import from another configuration", "options": {}},
#             "export": {"help": "Export to another configuration", "options": {}},
#             "reset": {"help": "Reset configuration to defaults", "options": {}},
#             "generate": {"help": "Generate command-line from config", "options": {}}
#         }
#     },
#     "llm": {
#         "help": "Manage LLM profiles",
#         "subcommands": {
#             "create": {
#                 "help": "Create a new LLM profile",
#                 "options": {
#                     "--name <n>": "Profile name",
#                     "--provider <PROV>": "LLM provider",
#                     "--model <MODEL>": "Model name",
#                     "--deployment <DEPL>": "Deployment name",
#                     "--api-key <KEY>": "API key",
#                     "--base-url <URL>": "Base URL for API",
#                     "--api-version <VER>": "API version",
#                     "--temperature <TEMP>": "Temperature (0.0-1.0)"
#                 }
#             },
#             "list": {
#                 "help": "List available LLM profiles",
#                 "options": {
#                     "--format <FORMAT>": "Output format (json, table)"
#                 }
#             },
#             "edit": {
#                 "help": "Edit an existing LLM profile",
#                 "options": {
#                     "--name <n>": "Profile name",
#                     "<same options as create>": ""
#                 }
#             },
#             "delete": {
#                 "help": "Delete an LLM profile",
#                 "options": {
#                     "--name <n>": "Profile name"
#                 }
#             },
#             "use": {
#                 "help": "Use a specific LLM profile",
#                 "options": {
#                     "--name <n>": "Profile name"
#                 }
#             },
#             "show": {
#                 "help": "Show LLM profile details",
#                 "options": {
#                     "--name <n>": "Profile name",
#                     "--format <FORMAT>": "Output format (json, yaml, table)"
#                 }
#             }
#         }
#     },
#     "help": {
#         "help": "Display help information",
#         "subcommands": {}
#     },
#     "schema": {
#         "help": "Display command structure tree",
#         "subcommands": {}
#     }
# }


@click.group(name="schema")
def schema_group():
    """Display command structure as ASCII art."""
    pass


@schema_group.command(name="show")
@click.argument("command", required=False)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def show_schema(command: str, verbose: bool):
    """Show schema for a specific command or the entire CLI."""
    # Ensure context is initialized
    try:
        ctx = ContextManager.get_instance()
    except RuntimeError:
        ctx = ContextManager.initialize({"verbose": verbose})
    
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