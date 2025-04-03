"""
Advanced runtime settings class for CLI tool.
Extends the basic runtime settings with parameter resolution capabilities.
"""

import os
import json
import click
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Set, Type
import copy

from .param_resolver import ParameterResolver
from .rtsettings import RTSettings
from .context import ContextManager

class AdvancedRTSettings(RTSettings):
    """
    Advanced runtime settings class that uses ParameterResolver for initialization.
    
    This class extends the base RTSettings class with advanced parameter resolution
    capabilities, allowing it to automatically resolve parameters from various sources
    based on the current Click context.
    """
    
    def __init__(self, cli_args: Optional[Dict[str, Any]] = None, resolver: Optional[ParameterResolver] = None):
        """
        Initialize advanced runtime settings with resolved parameters.
        
        Args:
            cli_args: Optional explicit command-line arguments to use
            resolver: Optional parameter resolver instance to use
        """
        # Use the resolver if provided, or create a new one
        self.resolver = resolver or ParameterResolver()
        
        # If cli_args are not provided, try to resolve from current Click context
        resolved_args = cli_args
        if resolved_args is None:
            try:
                # Try to get the current Click context
                ctx = click.get_current_context()
                # Resolve parameters using the resolver
                resolved_args = self.resolver.resolve_command_params(ctx)
            except RuntimeError:
                # No Click context available, use empty dict
                resolved_args = {}
        
        # Initialize the parent class with resolved arguments
        super().__init__(resolved_args)
        
        # Store the original command context for later use
        self.command_context = self._get_command_context()
        
        # Apply command-specific configurations
        self._apply_command_specific_config()
    
    def _get_command_context(self) -> Dict[str, Any]:
        """
        Get information about the current command context.
        
        Returns:
            Dictionary with command context information
        """
        command_context = {
            "command_path": None,
            "command_name": None,
            "parent_commands": [],
            "root_command": None
        }
        
        try:
            # Try to get the current Click context
            ctx = click.get_current_context()
            
            # Build command path and hierarchy
            commands = []
            current = ctx
            
            while current is not None:
                if current.info_name and current.info_name != 'cli':
                    commands.insert(0, current.info_name)
                if current.parent is None and current.info_name:
                    command_context["root_command"] = current.info_name
                current = current.parent
            
            if commands:
                command_context["command_path"] = ".".join(commands)
                command_context["command_name"] = commands[-1]
                if len(commands) > 1:
                    command_context["parent_commands"] = commands[:-1]
        except RuntimeError:
            # No Click context available, leave defaults
            pass
            
        return command_context
    
    def _apply_command_specific_config(self) -> None:
        """
        Apply command-specific configurations to the runtime context.
        
        This method looks for command-specific configurations in the
        effective configuration and applies them to the runtime context.
        """
        if not self.command_context.get("command_path"):
            return
            
        command_path = self.command_context["command_path"]
        
        # Check if there are command-specific configurations
        if "commands" in self.context and command_path in self.context["commands"]:
            # Get command-specific configurations
            cmd_config = self.context["commands"][command_path]
            
            # Apply command-specific configurations to cli_args
            for key, value in cmd_config.items():
                # Only apply if not already set by CLI arguments
                if key not in self.cli_args or self.cli_args[key] is None:
                    self.cli_args[key] = value
    
    def get_command_config(self, command_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get command-specific configuration settings.
        
        Args:
            command_path: Optional command path string (e.g., "generate.prompt").
                          If not provided, uses the current command path.
                          
        Returns:
            Dictionary of command-specific configuration settings
        """
        path = command_path or self.command_context.get("command_path")
        if not path:
            return {}
            
        if "commands" in self.context and path in self.context["commands"]:
            return self.context["commands"][path]
        
        return {}
    
    def get_param_value(self, param_name: str, default: Any = None) -> Any:
        """
        Get a parameter value from the most appropriate source.
        
        This method checks for the parameter value in this order:
        1. CLI arguments
        2. Command-specific configuration
        3. General settings
        4. Provided default value
        
        Args:
            param_name: The name of the parameter to get
            default: Default value to return if parameter not found
            
        Returns:
            Parameter value from the most appropriate source
        """
        # Check CLI arguments first
        if param_name in self.cli_args:
            return self.cli_args[param_name]
        
        # Check command-specific configuration
        cmd_config = self.get_command_config()
        if param_name in cmd_config:
            return cmd_config[param_name]
        
        # Check general settings
        if param_name in self.context["settings"]:
            return self.context["settings"][param_name]
        
        # Return default value
        return default
    
    def set_command_config(self, command_path: str, config: Dict[str, Any], scope: str) -> None:
        """
        Set command-specific configuration settings.
        
        Args:
            command_path: Command path string (e.g., "generate.prompt")
            config: Dictionary of configuration settings
            scope: Configuration scope ("global", "local", or "file")
        """
        effective_config = self.get_config(scope)
        
        # Ensure "commands" section exists
        if "commands" not in effective_config:
            effective_config["commands"] = {}
        
        # Set command configuration
        effective_config["commands"][command_path] = config
        
        # Save updated configuration
        self.save_config(effective_config, scope)
    
    def update_command_config(self, command_path: str, updates: Dict[str, Any], scope: str) -> Dict[str, Any]:
        """
        Update command-specific configuration settings.
        
        Args:
            command_path: Command path string (e.g., "generate.prompt")
            updates: Dictionary of configuration setting updates
            scope: Configuration scope ("global", "local", or "file")
            
        Returns:
            Updated command configuration
        """
        effective_config = self.get_config(scope)
        
        # Ensure "commands" section exists
        if "commands" not in effective_config:
            effective_config["commands"] = {}
        
        # Ensure command configuration exists
        if command_path not in effective_config["commands"]:
            effective_config["commands"][command_path] = {}
        
        # Update command configuration
        for key, value in updates.items():
            effective_config["commands"][command_path][key] = value
        
        # Save updated configuration
        self.save_config(effective_config, scope)
        
        return effective_config["commands"][command_path]
    
    def delete_command_config(self, command_path: str, scope: str) -> None:
        """
        Delete command-specific configuration settings.
        
        Args:
            command_path: Command path string (e.g., "generate.prompt")
            scope: Configuration scope ("global", "local", or "file")
        """
        effective_config = self.get_config(scope)
        
        # Check if commands section and command path exist
        if "commands" in effective_config and command_path in effective_config["commands"]:
            # Delete command configuration
            del effective_config["commands"][command_path]
            
            # Save updated configuration
            self.save_config(effective_config, scope)

class AdvancedContextManager(ContextManager):
    """
    Advanced context manager that uses AdvancedRTSettings.
    
    This class extends the base ContextManager to use AdvancedRTSettings
    for enhanced parameter resolution and command-specific configurations.
    """
    _advanced_instance = None
    _advanced_settings = None
    
    @classmethod
    def initialize_advanced(cls, cli_args: Optional[Dict[str, Any]] = None,
                           resolver: Optional[ParameterResolver] = None) -> 'AdvancedContextManager':
        """Initialize the advanced context manager with CLI arguments and resolver."""
        instance = cls()
        instance._advanced_settings = AdvancedRTSettings(cli_args, resolver)
        cls._advanced_instance = instance
        return instance
    
    @classmethod
    def get_advanced_instance(cls) -> 'AdvancedContextManager':
        """Get the singleton instance of the advanced context manager."""
        if cls._advanced_instance is None or cls._advanced_instance._advanced_settings is None:
            raise RuntimeError("AdvancedContextManager not initialized. Call initialize_advanced() first.")
        return cls._advanced_instance
    
    @property
    def advanced_settings(self) -> AdvancedRTSettings:
        """Get the advanced runtime settings object."""
        if self._advanced_settings is None:
            raise RuntimeError("Advanced runtime settings not initialized.")
        return self._advanced_settings

def initialize_advanced_context(cli_args: Optional[Dict[str, Any]] = None,
                              resolver: Optional[ParameterResolver] = None) -> AdvancedContextManager:
    """
    Initialize or get the advanced context manager instance.
    
    Args:
        cli_args: Optional explicit command-line arguments
        resolver: Optional parameter resolver
        
    Returns:
        Initialized AdvancedContextManager instance
    """
    try:
        # Try to get existing advanced context manager
        ctx = AdvancedContextManager.get_advanced_instance()
        
        # Update context if arguments provided
        if cli_args:
            # Create new settings with provided arguments
            ctx._advanced_settings = AdvancedRTSettings(cli_args, resolver)
        
        return ctx
    except RuntimeError:
        # Initialize new advanced context manager
        return AdvancedContextManager.initialize_advanced(cli_args, resolver)

def get_parameter_value(param_name: str, default: Any = None) -> Any:
    """
    Utility function to get a parameter value from the advanced context.
    
    This function tries to get a parameter value from the advanced context.
    If the advanced context is not initialized, it falls back to the regular context.
    
    Args:
        param_name: The name of the parameter to get
        default: Default value to return if parameter not found
        
    Returns:
        Parameter value from the most appropriate source
    """
    try:
        # Try to get from advanced context
        ctx = AdvancedContextManager.get_advanced_instance()
        return ctx.advanced_settings.get_param_value(param_name, default)
    except RuntimeError:
        # Fall back to regular context
        try:
            ctx = ContextManager.get_instance()
            settings = ctx.settings
            
            # Check CLI arguments
            if param_name in settings.cli_args:
                return settings.cli_args[param_name]
            
            # Check settings
            if param_name in settings.context["settings"]:
                return settings.context["settings"][param_name]
            
            return default
        except RuntimeError:
            # No context available
            return default