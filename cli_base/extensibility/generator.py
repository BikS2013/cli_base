# cli_base/extensibility/profile_command_generator.py
import click
from typing import Callable, Dict, List, Optional, Any, Type

from cli_base.commands.cmd_options import (
    json_format_option, json_input_argument, profile_name_option, 
    table_format_option, scope_options
)
from cli_base.utils.command_registry import CommandRegistry
from cli_base.utils.profiles import ProfileManager
from cli_base.commands.generic_profile_cmd import (
    create_profile, list_profiles, show_profile,
    edit_profile, delete_profile, use_profile
)

class ProfileCommandGenerator:
    """
    Generates a complete set of profile management commands based on a specification.
    """
    
    def __init__(
        self, 
        name: str,
        command_name: str,
        description: str,
        profile_params: List[Dict[str, Any]],
        profile_manager_factory: Callable[[], ProfileManager],
        help_texts: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a profile command generator.
        
        Args:
            name: The name of the profile type (e.g., "LLM", "Database")
            command_name: The command name in CLI (e.g., "llm", "db")
            description: The description for the command group
            profile_params: List of profile parameters specifications
            profile_manager_factory: Function that returns a profile manager instance
            help_texts: Optional custom help texts for commands
        """
        self.name = name
        self.command_name = command_name
        self.description = description
        self.profile_params = profile_params
        self.profile_manager_factory = profile_manager_factory
        self.help_texts = help_texts or {}
        
    def _get_help_text(self, command: str, default: str) -> str:
        """Get help text for a command, falling back to default if not specified."""
        return self.help_texts.get(command, default)
    
    def _create_profile_options(self) -> Callable:
        """Create decorator function for profile options."""
        def profile_options(command):
            """Decorator to add profile options to a command."""
            for param in self.profile_params:
                command = click.option(
                    f"--{param['name']}", 
                    type=param['type'], 
                    help=param['help'], 
                    required=param.get('required', False)   
                )(command)
            return command
        return profile_options
        
    def generate_command_group(self) -> click.Group:
        """Generate a complete command group for profile management."""
        profile_options = self._create_profile_options()
        
        @click.group(name=self.command_name)
        def command_group():
            """Command group for profile management."""
            pass
        
        command_group.__doc__ = self.description
        
        # Create command
        @command_group.command(name="create")
        @profile_options
        @scope_options
        @json_input_argument
        def create_cmd(json_input: Optional[str], **kwargs):
            """Create a new profile."""
            manager = self.profile_manager_factory()
            create_profile(self.name, manager, json_input, **kwargs)
        
        create_cmd.__doc__ = self._get_help_text("create", f"Create a new {self.name} profile.")
        
        # List command
        @command_group.command(name="list")
        @scope_options
        @table_format_option
        def list_cmd(scope: str, file_path: Optional[str], output_format: str):
            """List available profiles."""
            manager = self.profile_manager_factory()
            list_profiles(self.name, manager, self.profile_params, scope, file_path, output_format)
        
        list_cmd.__doc__ = self._get_help_text("list", f"List available {self.name} profiles.")
        
        # Show command
        @command_group.command(name="show")
        @profile_name_option
        @scope_options
        @json_format_option
        def show_cmd(name: str, scope: str, file_path: Optional[str], output_format: str):
            """Show profile details."""
            manager = self.profile_manager_factory()
            show_profile(self.name, manager, name, scope, file_path, output_format)
        
        show_cmd.__doc__ = self._get_help_text("show", f"Show {self.name} profile details.")
        
        # Edit command
        @command_group.command(name="edit")
        @profile_name_option
        @profile_options
        @scope_options
        @json_input_argument
        def edit_cmd(name: str, json_input: Optional[str], **kwargs):
            """Edit an existing profile."""
            manager = self.profile_manager_factory()
            edit_profile(self.name, manager, name, json_input, **kwargs)
        
        edit_cmd.__doc__ = self._get_help_text("edit", f"Edit an existing {self.name} profile.")
        
        # Delete command
        @command_group.command(name="delete")
        @profile_name_option
        @scope_options
        @click.confirmation_option(prompt="Are you sure you want to delete this profile?")
        def delete_cmd(name: str, scope: str, file_path: Optional[str]):
            """Delete a profile."""
            manager = self.profile_manager_factory()
            delete_profile(self.name, manager, name, scope, file_path)
        
        delete_cmd.__doc__ = self._get_help_text("delete", f"Delete a {self.name} profile.")
        
        # Use command
        @command_group.command(name="use")
        @profile_name_option
        @scope_options
        def use_cmd(name: str, scope: str, file_path: Optional[str]):
            """Use a specific profile as default."""
            manager = self.profile_manager_factory()
            use_profile(self.name, manager, name, scope, file_path)
        
        use_cmd.__doc__ = self._get_help_text("use", f"Use a specific {self.name} profile as default.")

        # Register command with registry
        registry = CommandRegistry.get_instance()
        schema = registry.extract_schema_from_command(self.command_name, command_group)
        registry.register_command(self.command_name, command_group, schema)
        
        return command_group
