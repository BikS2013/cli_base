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
                          command: Union[click.Group, click.Command], 
                          schema: Dict[str, Any]) -> None:
        """
        Register a command/command group and its schema.
        
        Args:
            command_name: The name of the command
            command: The Click command or command group object
            schema: Schema information for the command
        """
        self._commands[command_name] = command
        self._schemas[command_name] = schema
    
    def get_all_commands(self) -> Dict[str, Union[click.Group, click.Command]]:
        """Get all registered commands."""
        return self._commands
    
    def get_command(self, name: str) -> Optional[Union[click.Group, click.Command]]:
        """Get a command by name."""
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
    
    def extract_schema_from_command(self, command_name: str, command: Union[click.Group, click.Command]) -> Dict[str, Any]:
        """
        Extract schema information from a command or command group.
        
        This allows automatic schema generation for dynamically created commands.
        
        Args:
            command_name: The name of the command
            command: The Click command or command group object
            
        Returns:
            Schema dictionary for the command
        """
        # Get help text from command docstring
        help_text = command.help or f"Manage {command_name}"
        
        # Initialize schema
        schema = {
            "help": help_text,
            "subcommands": {}
        }
        
        # Check if this is a command group or a simple command
        if isinstance(command, click.Group) and hasattr(command, 'commands'):
            # Extract subcommands
            for subcmd_name, subcmd in command.commands.items():
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
        else:
            # For simple commands, add options directly to the main schema
            options_schema = {}
            for param in command.params:
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
                        options_schema[option_name] = param.help or ""
            
            # Add options to the main schema
            schema["options"] = options_schema
        
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
            # Extract schema for both groups and simple commands
            schema = self.extract_schema_from_command(cmd_name, cmd)
            # Register command or command group
            self.register_command(cmd_name, cmd, schema)