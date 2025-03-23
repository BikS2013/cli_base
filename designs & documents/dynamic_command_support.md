# Supporting Dynamically Generated Commands

This document outlines the necessary changes to make the CLI's schema and help commands work with dynamically generated command groups created by the ProfileCommandGenerator.

## Current Limitations

Currently, the schema and help commands rely on statically defined data:

1. The `schema_cmd.py` module has a hardcoded `SCHEMA_DATA` dictionary
2. The `help_command` in `main.py` relies on the Click context and command structure

These approaches don't work well with dynamically generated commands because:
- Schema data becomes outdated when new command types are added
- Help text may not reflect customized descriptions from dynamically generated commands

## Proposed Solution

We'll implement a command registry system that:
1. Tracks all command groups (both static and dynamic)
2. Provides access to their schema and help information
3. Automatically updates when new command groups are added

## Implementation Steps

### 1. Create a Command Registry

First, let's create a registry to track all commands:

```python
# cli_base/utils/command_registry.py
import click
from typing import Dict, List, Optional, Any, Callable, Set, Union
import inspect

class CommandRegistry:
    """
    Registry for tracking CLI commands and their schema information.
    
    This singleton class maintains a centralized registry of all commands,
    including dynamically generated ones, and provides access to their
    schema and help information.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'CommandRegistry':
        """Get the singleton instance of the registry."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the command registry."""
        if CommandRegistry._instance is not None:
            raise RuntimeError("CommandRegistry is a singleton. Use get_instance() instead.")
        
        self._commands = {}
        self._schemas = {}
        
    def register_command(self, 
                          command_name: str, 
                          command_group: click.Group, 
                          schema: Dict[str, Any]) -> None:
        """
        Register a command group and its schema.
        
        Args:
            command_name: The name of the command
            command_group: The Click command group object
            schema: Schema information for the command
        """
        self._commands[command_name] = command_group
        self._schemas[command_name] = schema
    
    def get_all_commands(self) -> Dict[str, click.Group]:
        """Get all registered command groups."""
        return self._commands
    
    def get_command(self, name: str) -> Optional[click.Group]:
        """Get a command group by name."""
        return self._commands.get(name)
    
    def get_schema(self, name: str = None) -> Dict[str, Any]:
        """
        Get schema information for a command or all commands.
        
        Args:
            name: Command name to get schema for, or None for all schemas
            
        Returns:
            Schema dictionary for the specified command or all commands
        """
        if name is not None:
            return {name: self._schemas.get(name, {})}
        return self._schemas
    
    def extract_schema_from_command(self, command_name: str, command_group: click.Group) -> Dict[str, Any]:
        """
        Extract schema information from a command group.
        
        This allows automatic schema generation for dynamically created commands.
        
        Args:
            command_name: The name of the command
            command_group: The Click command group object
            
        Returns:
            Schema dictionary for the command
        """
        # Get help text from command docstring
        help_text = command_group.help or f"Manage {command_name}"
        
        # Initialize schema
        schema = {
            "help": help_text,
            "subcommands": {}
        }
        
        # Extract subcommands
        for subcmd_name, subcmd in command_group.commands.items():
            # Get subcommand help text
            subcmd_help = subcmd.help or f"{subcmd_name.capitalize()} {command_name}"
            
            # Initialize subcommand schema
            subcmd_schema = {
                "help": subcmd_help,
                "options": {}
            }
            
            # Extract parameters
            for param in subcmd.params:
                if isinstance(param, click.Option):
                    # Format option name
                    names = param.opts
                    if names:
                        name = names[0]  # Use the first option name (usually the long form)
                        # Add type hint for display
                        type_hint = ""
                        if param.type:
                            if hasattr(param.type, 'name'):
                                type_hint = f"<{param.type.name.upper()}>"
                            else:
                                type_hint = f"<{param.type.__name__.upper()}>"
                        
                        # Add formatted option to schema
                        option_name = f"{name} {type_hint}" if type_hint else name
                        subcmd_schema["options"][option_name] = param.help or ""
            
            # Add subcommand to schema
            schema["subcommands"][subcmd_name] = subcmd_schema
        
        return schema
    
    def register_commands_from_cli(self, cli: click.Group) -> None:
        """
        Register all commands from a CLI group.
        
        This method recursively extracts and registers all commands
        and their schemas from a Click CLI group.
        
        Args:
            cli: The main Click CLI group
        """
        for cmd_name, cmd in cli.commands.items():
            if isinstance(cmd, click.Group):
                # Extract schema
                schema = self.extract_schema_from_command(cmd_name, cmd)
                # Register command
                self.register_command(cmd_name, cmd, schema)
```

### 2. Register Commands from ProfileCommandGenerator

Now we need to modify the ProfileCommandGenerator to register its commands:

```python
# Update cli_base/extensibility/profile_command_generator.py

from cli_base.utils.command_registry import CommandRegistry

class ProfileCommandGenerator:
    # ... existing code ...
    
    def generate_command_group(self) -> click.Group:
        """Generate a complete command group for profile management."""
        # ... existing code to create command_group ...
        
        # Register command with registry
        registry = CommandRegistry.get_instance()
        schema = registry.extract_schema_from_command(self.command_name, command_group)
        registry.register_command(self.command_name, command_group, schema)
        
        return command_group
```

### 3. Update the Schema Command

Now, let's update the schema command to use the registry:

```python
# cli_base/commands/schema_cmd.py
import click
from ..utils.context import ContextManager
from ..utils.formatting import OutputFormatter
from ..utils.command_registry import CommandRegistry


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
```

### 4. Update the Help Command

Finally, we need to update the help command in main.py:

```python
# Update in cli_base/main.py
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
```

### 5. Initialize the Registry in the Main CLI Function

Finally, we need to initialize the registry with all commands when the CLI starts:

```python
# Update in cli_base/main.py
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
        
    # Register all commands with the registry
    # This should be done after all commands are added to the CLI
    # so we'll call this function after adding all commands

# Add command groups
cli.add_command(config_group)
cli.add_command(llm_group)
cli.add_command(schema_group)
# Add other profile command groups here

# Now register all commands
from cli_base.utils.command_registry import CommandRegistry
registry = CommandRegistry.get_instance()
registry.register_commands_from_cli(cli)
```

## Creating New Profile Commands

With these changes, when you create new profile commands using the ProfileCommandGenerator, they will automatically be registered with the CommandRegistry, and their schema and help information will be available to the schema and help commands.

Here's the updated workflow for adding a new profile type:

1. Define your profile parameters and manager class
2. Use ProfileCommandGenerator to create a command group
3. Add the command group to the CLI with `cli.add_command()`

That's it! The schema and help commands will automatically pick up the new command and display the correct information.

## Example: Adding a New Database Profile Command

```python
# In your database.py module
db_command_generator = ProfileCommandGenerator(
    name="Database",
    command_name="db",
    description="Manage database connection profiles.",
    profile_params=DB_PROFILE_PARAMS,
    profile_manager_factory=get_database_profile_manager,
    help_texts={...}
)

# Generate the command group
db_group = db_command_generator.generate_command_group()

# In main.py
from cli_base.extensibility.database import db_group
cli.add_command(db_group)
```

Now when you run:
- `cli-tool schema show db` - It will show the database command schema
- `cli-tool help db` - It will show the database command help text

## Benefits of This Approach

1. **Automatic Schema Generation**: Schema information is automatically extracted and doesn't need to be manually maintained
2. **Dynamic Command Support**: Works with both static and dynamic commands
3. **Consistent Help Text**: All commands (static and dynamic) use the same help system
4. **Extensibility**: Makes it easy to add new command types without modifying schema or help code
5. **Better Maintainability**: Centralizes command registration and schema generation

## Implementation Considerations

1. **Registration Timing**: Commands need to be registered after they're added to the CLI but before they're used
2. **Help Text Quality**: The quality of automatically generated schema depends on good docstrings and parameter descriptions
3. **Performance**: Schema extraction adds a small overhead during CLI startup, but it's negligible for most use cases
4. **Compatibility**: This approach is compatible with Click's existing help system