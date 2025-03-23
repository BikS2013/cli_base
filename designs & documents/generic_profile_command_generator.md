# Generic Profile Command System Design

## Overview

This document outlines a comprehensive approach to fully generalize profile-based commands in the CLI tool. Building on your existing work with the LLM command module, this system will allow you to quickly implement new profile-based command groups (such as database connections, API credentials, or environment configurations) by minimizing duplication and maximizing reuse.

## Design Goals

1. **Minimal Boilerplate**: New profile types should require minimal code to implement
2. **Consistent Interface**: All profile commands should have the same structure and behavior
3. **Type Safety**: Maintain strong typing throughout the system
4. **Extensibility**: Easy to add new profile types with custom validation logic
5. **Maintainability**: Centralize common code to reduce duplication

## Implementation Strategy

### 1. Create a Profile Command Generator

Create a new module that generates complete command groups for profile management:

```python
# cli_base/extensibility/profile_command_generator.py
import click
from typing import Callable, Dict, List, Optional, Any, Type

from cli_base.commands.cmd_options import (
    json_format_option, json_input_argument, profile_name_option, 
    table_format_option, scope_options
)
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
        
        return command_group
```

### 2. Create a Base Profile Manager

The base profile manager abstract class will define the interface for all profile managers:

```python
# cli_base/utils/profiles.py (Update the existing file)

from typing import Any, Dict, List, Optional, TypedDict

class ProfileSpec(TypedDict, total=False):
    """Type specification for profile parameters."""
    name: str
    type: type
    help: str
    required: bool

class ProfileValidationResult(TypedDict):
    """Result of profile validation."""
    valid: bool
    errors: List[str]
    profile: Dict[str, Any]

class BaseProfileManager(ProfileManager):
    """Base class for profile managers with extended validation capabilities."""
    
    def __init__(self, profile_type: str, profile_params: List[ProfileSpec]):
        """
        Initialize a profile manager.
        
        Args:
            profile_type: The profile type identifier used in config
            profile_params: Profile parameter specifications
        """
        super().__init__(profile_type)
        self.profile_params = profile_params
        
    def validate_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a profile against the parameter specifications.
        
        This base implementation checks required fields and applies defaults.
        Subclasses may override to add additional validation.
        
        Args:
            profile: The profile data to validate
            
        Returns:
            The validated and normalized profile data
            
        Raises:
            ValueError: If validation fails
        """
        # Check required fields
        required_fields = [param["name"] for param in self.profile_params if param.get("required", False)]
        for field in required_fields:
            if field not in profile:
                raise ValueError(f"Missing required field: {field}")
        
        # Apply field-specific validation (to be implemented by subclasses)
        validation_result = self._validate_field_values(profile)
        if not validation_result["valid"]:
            raise ValueError(", ".join(validation_result["errors"]))
            
        # Apply defaults
        normalized_profile = self._apply_default_values(validation_result["profile"])
        
        return normalized_profile
    
    def _validate_field_values(self, profile: Dict[str, Any]) -> ProfileValidationResult:
        """
        Validate field values beyond basic required field checking.
        
        Subclasses should override this method to implement 
        field-specific validation logic.
        
        Args:
            profile: The profile data to validate
            
        Returns:
            Validation result including errors and normalized profile
        """
        # Base implementation just passes through
        return {
            "valid": True,
            "errors": [],
            "profile": profile 
        }
    
    def _apply_default_values(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply default values for optional fields.
        
        Subclasses should override this method to apply any
        default values for optional fields.
        
        Args:
            profile: The profile data to apply defaults to
            
        Returns:
            Profile with defaults applied
        """
        # Base implementation just returns the profile as-is
        return profile
    
    def create_profile(self, profile_data: Dict[str, Any], scope: str) -> Dict[str, Any]:
        """Create a new profile with validation."""
        validated_profile = self.validate_profile(profile_data)
        return super().create_profile(validated_profile, scope)
        
    def edit_profile(self, name: str, updates: Dict[str, Any], scope: str) -> Dict[str, Any]:
        """Edit a profile with validation."""
        # First, get the existing profile
        existing = self.get_profile_from_scope(name, scope)
        
        # Merge updates with existing profile
        merged = {**existing, **updates}
        
        # Validate the merged profile
        validated = self.validate_profile(merged)
        
        return super().edit_profile(name, validated, scope)
```

### 3. Example Implementation for LLM Profiles

Here's how you can refactor your LLM module to use this new architecture:

```python
# cli_base/extensibility/llm.py
from typing import Any, Dict

from cli_base.utils.profiles import BaseProfileManager, ProfileValidationResult
from cli_base.extensibility.profile_command_generator import ProfileCommandGenerator

# Define profile parameters
PROFILE_PARAMS = [
    {"name": "name", "type": str, "help": "Profile name", "required": True},
    {"name": "provider", "type": str, "help": "LLM provider (e.g., openai, anthropic)", "required": True},
    {"name": "model", "type": str, "help": "Model name", "required": True},
    {"name": "deployment", "type": str, "help": "Deployment name (for Azure)", "required": False},
    {"name": "api_key", "type": str, "help": "API key", "required": True},
    {"name": "base_url", "type": str, "help": "Base URL for API", "required": False},
    {"name": "api_version", "type": str, "help": "API version", "required": False},
    {"name": "temperature", "type": float, "help": "Temperature (0.0-1.0)", "required": False}
]

class LLMProfileManager(BaseProfileManager):
    """Specialized profile manager for LLM profiles."""

    def __init__(self):
        """Initialize an LLM profile manager."""
        super().__init__("llm", PROFILE_PARAMS)
    
    def _validate_field_values(self, profile: Dict[str, Any]) -> ProfileValidationResult:
        """Validate LLM-specific field values."""
        errors = []
        
        # Validate temperature range if specified
        if "temperature" in profile:
            temp = profile["temperature"]
            if not 0.0 <= temp <= 1.0:
                errors.append("Temperature must be between 0.0 and 1.0")
        
        # Validate provider
        if "provider" in profile:
            provider = profile["provider"]
            valid_providers = ["openai", "anthropic", "azure", "cohere"]
            if provider not in valid_providers:
                errors.append(f"Provider must be one of: {', '.join(valid_providers)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "profile": profile
        }
    
    def _apply_default_values(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values for LLM profiles."""
        defaults = {
            "deployment": None,
            "base_url": self._get_default_base_url(profile.get("provider")),
            "api_version": "v1",
            "temperature": 0.7
        }
        
        for field, default_value in defaults.items():
            if field not in profile:
                profile[field] = default_value
                
        return profile
    
    def _get_default_base_url(self, provider: str) -> str:
        """Get the default base URL for a provider."""
        providers = {
            "openai": "https://api.openai.com",
            "anthropic": "https://api.anthropic.com",
            "azure": "https://YOUR_RESOURCE_NAME.openai.azure.com",
            "cohere": "https://api.cohere.ai"
        }
        return providers.get(provider, "")

# Create a factory function for the profile manager
def get_llm_profile_manager() -> LLMProfileManager:
    """Factory function to create an LLM profile manager."""
    return LLMProfileManager()

# Create a command generator
llm_command_generator = ProfileCommandGenerator(
    name="LLM",
    command_name="llm",
    description="Manage LLM (Large Language Model) profiles.",
    profile_params=PROFILE_PARAMS,
    profile_manager_factory=get_llm_profile_manager,
    help_texts={
        "create": "Create a new LLM profile with provider, model, and API key settings.",
        "list": "List all available LLM profiles.",
        "show": "Show details for a specific LLM profile.",
        "edit": "Edit an existing LLM profile.",
        "delete": "Delete an LLM profile.",
        "use": "Set a specific LLM profile as the default."
    }
)

# Generate the command group
llm_group = llm_command_generator.generate_command_group()
```

### 4. Simplified main.py Integration

With this approach, adding new command groups to `main.py` becomes trivial:

```python
# cli_base/main.py
import click
from cli_base.commands.config_cmd import config_group
from cli_base.commands.schema_cmd import schema_group
from cli_base.extensibility.llm import llm_group
# Import other profile command groups here

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
```

## Example: Adding a New Profile Type

To demonstrate how easy it is to add a new profile type, let's implement database connection profiles:

```python
# cli_base/extensibility/database.py
from typing import Any, Dict
from cli_base.utils.profiles import BaseProfileManager, ProfileValidationResult
from cli_base.extensibility.profile_command_generator import ProfileCommandGenerator

# Define database profile parameters
DB_PROFILE_PARAMS = [
    {"name": "name", "type": str, "help": "Profile name", "required": True},
    {"name": "type", "type": str, "help": "Database type (mysql, postgres, sqlite)", "required": True},
    {"name": "host", "type": str, "help": "Database host", "required": False},
    {"name": "port", "type": int, "help": "Database port", "required": False},
    {"name": "username", "type": str, "help": "Database username", "required": False},
    {"name": "password", "type": str, "help": "Database password", "required": False},
    {"name": "database", "type": str, "help": "Database name", "required": True},
    {"name": "ssl", "type": bool, "help": "Use SSL connection", "required": False},
]

class DatabaseProfileManager(BaseProfileManager):
    """Profile manager for database connections."""
    
    def __init__(self):
        """Initialize a database profile manager."""
        super().__init__("database", DB_PROFILE_PARAMS)
    
    def _validate_field_values(self, profile: Dict[str, Any]) -> ProfileValidationResult:
        """Validate database-specific fields."""
        errors = []
        
        # Validate database type
        if "type" in profile:
            db_type = profile["type"]
            valid_types = ["mysql", "postgres", "sqlite", "mongodb"]
            if db_type not in valid_types:
                errors.append(f"Database type must be one of: {', '.join(valid_types)}")
        
        # Validate that host and port are provided for remote databases
        if "type" in profile and profile["type"] != "sqlite":
            if "host" not in profile or not profile["host"]:
                errors.append("Host is required for non-SQLite databases")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "profile": profile
        }
    
    def _apply_default_values(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values based on database type."""
        db_type = profile.get("type")
        
        # Set type-specific defaults
        if db_type == "mysql":
            defaults = {"port": 3306, "ssl": False}
        elif db_type == "postgres":
            defaults = {"port": 5432, "ssl": False}
        elif db_type == "mongodb":
            defaults = {"port": 27017, "ssl": False}
        elif db_type == "sqlite":
            defaults = {"host": None, "port": None, "username": None, "password": None, "ssl": False}
        else:
            defaults = {"ssl": False}
        
        # Apply defaults
        for field, default in defaults.items():
            if field not in profile:
                profile[field] = default
                
        return profile

def get_database_profile_manager() -> DatabaseProfileManager:
    """Factory function for database profile manager."""
    return DatabaseProfileManager()

# Create a command generator for database profiles
db_command_generator = ProfileCommandGenerator(
    name="Database",
    command_name="db",
    description="Manage database connection profiles.",
    profile_params=DB_PROFILE_PARAMS,
    profile_manager_factory=get_database_profile_manager,
    help_texts={
        "create": "Create a new database connection profile.",
        "list": "List all available database connection profiles.",
        "show": "Show details for a specific database connection profile.",
        "edit": "Edit an existing database connection profile.",
        "delete": "Delete a database connection profile.",
        "use": "Set a specific database profile as the default."
    }
)

# Generate the command group
db_group = db_command_generator.generate_command_group()
```

Then in `main.py`, simply add:

```python
from cli_base.extensibility.database import db_group
# ...
cli.add_command(db_group)
```

## Benefits of This Approach

1. **Centralized Logic**: All command generation logic is in one place
2. **Type Safety**: Strong typing throughout with TypedDict
3. **Extended Validation**: Rich validation capabilities in the base manager
4. **Minimal Duplication**: New profile types need very little code
5. **Consistency**: All profile commands have the same structure and behavior
6. **Declarative Style**: Profile types are defined declaratively with parameters
7. **Custom Help Text**: Easy to provide custom help text for commands

## Implementation Roadmap

1. Create the `ProfileCommandGenerator` class
2. Enhance the `ProfileManager` to include the new validation capabilities
3. Refactor the LLM module to use the new approach
4. Add tests for the new components
5. Document the new architecture

This design provides a flexible, reusable foundation for adding any type of profile-based command to your CLI tool, while maintaining consistency and reducing code duplication.