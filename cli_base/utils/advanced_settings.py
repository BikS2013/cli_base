"""
Advanced runtime settings class for CLI tool.
Provides comprehensive parameter resolution for CLI commands.
"""

import os
import json
import click
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Set, Type
import copy

from .param_resolver import ParameterResolver
from .context import initialize_context

class AdvancedRTSettings:
    """
    Advanced runtime settings class that uses ParameterResolver for initialization.
    
    This class handles all the runtime settings for the CLI application with
    advanced parameter resolution capabilities.
    """

    DEFAULT_CONFIG = {
        "profiles": {
            "llm": {},
            "database": {}
        },
        "defaults": {
            "llm": None,
            "database": None
        },
        "settings": {
            "output_format": "json",
            "color_theme": "dark",
            "log_level": "info"
        },
        "commands": {
            # Command-specific default parameters
            # For example:
            # "generate.prompt": {
            #     "stream": True,
            #     "temperature": 0.7
            # }
        }
    }
    
    def __init__(self, cli_args: Optional[Dict[str, Any]] = None, resolver: Optional[ParameterResolver] = None):
        """
        Initialize advanced runtime settings with resolved parameters.
        
        Args:
            cli_args: Optional explicit command-line arguments to use
            resolver: Optional parameter resolver instance to use
        """
        # Initialize file paths
        self.global_config_dir = Path.home() / ".cli-tool"
        self.global_config_path = self.global_config_dir / "config.json"
        self.local_config_dir = Path.cwd() / ".cli-tool"
        self.local_config_path = self.local_config_dir / "config.json"
        
        # Initialize configuration containers
        self.global_config = self.DEFAULT_CONFIG.copy()
        self.local_config = self.DEFAULT_CONFIG.copy()
        self.named_config = None
        self.named_config_path = None
        
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
        
        # Store CLI arguments
        self.cli_args = resolved_args or {}
        
        # Add system arguments to CLI args for better flag checking
        import sys
        self.cli_args["sys.argv"] = sys.argv
        
        # Verbose and quiet flags from CLI
        self.verbose = self.cli_args.get("verbose", False)
        self.quiet = self.cli_args.get("quiet", False)
        
        # Runtime context for commands
        self.context = {}
        
        # Initialize configuration files and load settings
        self._initialize_config_files()
        self._load_configurations()
        self._build_runtime_context()
        
        # Store the original command context for later use
        self.command_context = self._get_command_context()
        
        # Apply command-specific configurations
        self._apply_command_specific_config()
    
    def _initialize_config_files(self):
        """Create default config directories and files if they don't exist."""
        # Global config
        if not self.global_config_dir.exists():
            self.global_config_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.global_config_path.exists():
            with open(self.global_config_path, 'w') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=2)
        
        # Local config directory (but don't create file automatically)
        if not self.local_config_dir.exists():
            self.local_config_dir.mkdir(parents=True, exist_ok=True)

    def _load_configurations(self):
        """Load all configuration files according to precedence rules."""
        # Load global config
        if self.global_config_path.exists():
            try:
                with open(self.global_config_path, 'r') as f:
                    self.global_config = json.load(f)
            except json.JSONDecodeError:
                # Keep default if global config is invalid
                pass
        
        # Load local config
        if self.local_config_path.exists():
            try:
                with open(self.local_config_path, 'r') as f:
                    self.local_config = json.load(f)
            except json.JSONDecodeError:
                # Keep default if local config is invalid
                pass
        
        # Load named config if specified in CLI args
        file_path = self.cli_args.get("file_path")
        if file_path:
            self.named_config_path = Path(os.path.expanduser(file_path))
            if self.named_config_path.exists():
                try:
                    with open(self.named_config_path, 'r') as f:
                        self.named_config = json.load(f)
                except json.JSONDecodeError:
                    # Keep None if named config is invalid
                    self.named_config = None
    
    def _build_runtime_context(self):
        """
        Build the runtime context by merging configurations according to precedence rules
        based on which configuration scope options are specified:
        
        If --file option is used:
            1. Command line arguments
            2. Named configuration file
            3. Local configuration (for missing elements)
            4. Global configuration (for missing elements)
            5. Default values
            
        If --local option is used:
            1. Command line arguments
            2. Local configuration
            3. Global configuration (for missing elements)
            4. Default values
            
        If --global option is used:
            1. Command line arguments
            2. Global configuration
            3. Default values
            
        Default (no option specified):
            1. Command line arguments
            2. Local configuration
            3. Global configuration
            4. Default values
        """
        # Start with defaults
        runtime_config = self.DEFAULT_CONFIG.copy()
        
        # Determine current scope by checking system arguments directly
        # This is more reliable than checking the resolved parameters
        sys_argv = self.cli_args.get('sys.argv', [])
        sys_argv_str = ' '.join(sys_argv)
        
        # Check for global flag
        use_global = False
        if '--global' in sys_argv_str:
            use_global = True
        
        # Check for file flag
        use_file = False
        file_path = None
        if '--file' in sys_argv_str:
            use_file = True
            try:
                file_index = sys_argv.index('--file')
                if file_index + 1 < len(sys_argv):
                    file_path = sys_argv[file_index + 1]
            except (ValueError, IndexError):
                pass
        
        # Also check if scope and file parameters are set through other means
        current_scope = self.cli_args.get("scope", "local")
        if current_scope == "global":
            use_global = True
            
        cli_file_path = self.cli_args.get("file_path")
        if cli_file_path:
            use_file = True
            file_path = cli_file_path
        
        from .formatting import OutputFormatter
        if self.verbose:
            OutputFormatter.print_info(f"Using global: {use_global}")
            OutputFormatter.print_info(f"Using file: {use_file}, path: {file_path}")
            OutputFormatter.print_info(f"Current scope: {current_scope}")
            OutputFormatter.print_info(f"CLI args: {self.cli_args}")
            
        has_file_option = use_file and file_path is not None
        
        # If we have a file path but the named_config wasn't loaded, try loading it again
        if has_file_option and file_path and not self.named_config:
            self.named_config_path = Path(os.path.expanduser(file_path))
            if self.named_config_path.exists():
                try:
                    with open(self.named_config_path, 'r') as f:
                        self.named_config = json.load(f)
                    if self.verbose:
                        OutputFormatter.print_info(f"Loaded named config from {file_path}")
                except (json.JSONDecodeError, IOError) as e:
                    if self.verbose:
                        OutputFormatter.print_error(f"Error loading named config: {str(e)}")
                    # Keep None if named config is invalid or can't be read
                    self.named_config = None
        
        # Build config according to specified scope
        if has_file_option:
            # --file option: file -> local -> global -> defaults
            if self.named_config:
                runtime_config = self._deep_merge(runtime_config, self.global_config)
                runtime_config = self._deep_merge(runtime_config, self.local_config)
                runtime_config = self._deep_merge(runtime_config, self.named_config)
                self.context = runtime_config
                self.context["current_scope"] = "file"
                if self.verbose:
                    from .formatting import OutputFormatter
                    OutputFormatter.print_info(f"Using FILE configuration: {file_path}")
            else:
                # If named config not found, fall back to standard precedence
                runtime_config = self._deep_merge(runtime_config, self.global_config)
                runtime_config = self._deep_merge(runtime_config, self.local_config)
                self.context = runtime_config
                self.context["current_scope"] = "local"
                if self.verbose:
                    from .formatting import OutputFormatter
                    OutputFormatter.print_error(f"File configuration not found: {file_path}, using LOCAL configuration as fallback")
        elif use_global:
            # --global option: only global -> defaults
            runtime_config = self._deep_merge(runtime_config, self.global_config)
            self.context = runtime_config
            self.context["current_scope"] = "global"
            if self.verbose:
                OutputFormatter.print_info("Using GLOBAL configuration")
        else:
            # --local option or default: local -> global -> defaults
            runtime_config = self._deep_merge(runtime_config, self.global_config)
            runtime_config = self._deep_merge(runtime_config, self.local_config)
            self.context = runtime_config
            self.context["current_scope"] = "local"
            if self.verbose:
                OutputFormatter.print_info("Using LOCAL configuration")
        
        # Add CLI args to context
        self.context["cli_args"] = self.cli_args
    
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
    
    def get_config_path(self, scope: str) -> Path:
        """Get the path to the configuration file based on scope."""
        if scope == "global":
            return self.global_config_path
        elif scope == "local":
            return self.local_config_path
        elif scope == "file" and self.named_config_path:
            return self.named_config_path
        else:
            raise ValueError(f"Invalid scope: {scope}")

    def get_config(self, scope: str) -> Dict[str, Any]:
        """Get configuration by scope."""
        if scope == "global":
            return self.global_config
        elif scope == "local":
            return self.local_config
        elif scope == "file" and self.named_config:
            return self.named_config
        else:
            raise ValueError(f"Invalid scope: {scope}")

    def save_config(self, config: Dict[str, Any], scope: str) -> None:
        """Save configuration to the specified scope."""
        config_path = self.get_config_path(scope)
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Update runtime settings
        if scope == "global":
            self.global_config = config
        elif scope == "local":
            self.local_config = config
        elif scope == "file":
            self.named_config = config
        
        # Rebuild runtime context
        self._build_runtime_context()

    def update_config(self, updates: Dict[str, Any], scope: str) -> Dict[str, Any]:
        """Update configuration with new values, preserving existing structure."""
        config = self.get_config(scope)
        
        # Helper function to recursively update nested dictionaries
        updated_config = self._deep_merge(config, updates)
        self.save_config(updated_config, scope)
        return updated_config

    def get_effective_config(self) -> Dict[str, Any]:
        """Get the effective configuration considering all precedence rules."""
        return self.context

    def get_profile(self, profile_type: str, name: str) -> Dict[str, Any]:
        """Get a specific profile from the effective configuration."""
        if profile_type not in self.context["profiles"]:
            raise ValueError(f"Profile type not found: {profile_type}")
        
        if name not in self.context["profiles"][profile_type]:
            raise ValueError(f"Profile not found: {name}")
        
        return self.context["profiles"][profile_type][name]
    
    def get_profile_from_any_scope(self, profile_type: str, name: str) -> Dict[str, Any]:
        """
        Get a specific profile from any available scope, following precedence rules.
        
        This method will first check the current scope, then fall back to
        local, then global configurations looking for a profile with the given name.
        
        Args:
            profile_type: The type of profile to get
            name: The name of the profile to get
            
        Returns:
            The profile data
            
        Raises:
            ValueError: If the profile is not found in any scope
        """
        # First check effective merged configuration
        try:
            return self.get_profile(profile_type, name)
        except ValueError:
            # Not in effective config, check specific scopes
            current_scope = self.context.get("current_scope")
            
            # Try specific scopes based on current scope
            if current_scope == "file":
                # Try local scope next
                try:
                    if (profile_type in self.local_config["profiles"] and 
                        name in self.local_config["profiles"][profile_type]):
                        return self.local_config["profiles"][profile_type][name]
                except (KeyError, TypeError):
                    pass
                    
            # Finally try global scope
            try:
                if (profile_type in self.global_config["profiles"] and 
                    name in self.global_config["profiles"][profile_type]):
                    return self.global_config["profiles"][profile_type][name]
            except (KeyError, TypeError):
                pass
                
        # Not found in any scope
        raise ValueError(f"Profile '{name}' not found in any configuration scope")

    def get_profiles(self, profile_type: str, scope: str = None) -> Dict[str, Dict[str, Any]]:
        """Get all profiles of a specific type, optionally filtered by scope."""
        if scope:
            config = self.get_config(scope)
            if profile_type not in config["profiles"]:
                return {}
            return config["profiles"][profile_type]
        else:
            if profile_type not in self.context["profiles"]:
                return {}
            return self.context["profiles"][profile_type]

    def get_default_profile(self, profile_type: str) -> Optional[str]:
        """
        Get the name of the default profile for a specific type.
        
        Checks the effective configuration (merged from all scopes)
        for a default profile of the given type.
        """
        return self.context["defaults"].get(profile_type)
    
    def get_default_profile_from_any_scope(self, profile_type: str) -> Optional[str]:
        """
        Get the name of the default profile from any scope, following the precedence rules.
        
        This method will first check the current scope, then fall back to local,
        then global configurations looking for a default profile of the given type.
        """
        # First check effective merged configuration
        default_profile = self.context["defaults"].get(profile_type)
        if default_profile:
            return default_profile
            
        # Check specific scopes if not found in effective configuration
        current_scope = self.context.get("current_scope")
        
        # If current scope is "file" and no default was found, check local scope
        if current_scope == "file" and not default_profile:
            if profile_type in self.local_config["defaults"] and self.local_config["defaults"][profile_type]:
                return self.local_config["defaults"][profile_type]
                
        # Finally check global scope if still not found
        if not default_profile:
            if profile_type in self.global_config["defaults"] and self.global_config["defaults"][profile_type]:
                return self.global_config["defaults"][profile_type]
                
        return None

    def set_default_profile(self, profile_type: str, name: str, scope: str) -> None:
        """Set a profile as the default for its type in the specified scope."""
        config = self.get_config(scope)
        
        if profile_type not in config["profiles"]:
            raise ValueError(f"Profile type not found: {profile_type}")
        
        if name not in config["profiles"][profile_type]:
            raise ValueError(f"Profile not found: {name}")
        
        config["defaults"][profile_type] = name
        self.save_config(config, scope)

    def create_profile(self, profile_type: str, profile: Dict[str, Any], scope: str) -> None:
        """Create a new profile in the specified configuration."""
        config = self.get_config(scope)
        
        if profile_type not in config["profiles"]:
            config["profiles"][profile_type] = {}
        
        if profile.get("name") in config["profiles"][profile_type]:
            raise ValueError(f"Profile already exists: {profile.get('name')}")
        
        config["profiles"][profile_type][profile.get("name")] = profile
        self.save_config(config, scope)

    def edit_profile(self, profile_type: str, name: str, updates: Dict[str, Any], scope: str) -> Dict[str, Any]:
        """Edit an existing profile in the configuration."""
        config = self.get_config(scope)
        
        if profile_type not in config["profiles"]:
            raise ValueError(f"Profile type not found: {profile_type}")
        
        if name not in config["profiles"][profile_type]:
            raise ValueError(f"Profile not found: {name}")
        
        # Update profile
        config["profiles"][profile_type][name].update(updates)
        self.save_config(config, scope)
        return config["profiles"][profile_type][name]

    def delete_profile(self, profile_type: str, name: str, scope: str) -> None:
        """Delete a profile from the configuration."""
        config = self.get_config(scope)
        
        if profile_type not in config["profiles"]:
            raise ValueError(f"Profile type not found: {profile_type}")
        
        if name not in config["profiles"][profile_type]:
            raise ValueError(f"Profile not found: {name}")
        
        # Delete profile
        del config["profiles"][profile_type][name]
        
        # If this was the default profile, clear the default
        if config["defaults"].get(profile_type) == name:
            config["defaults"][profile_type] = None
        
        self.save_config(config, scope)

    def get_setting(self, setting_name: str, default: Any = None) -> Any:
        """Get a setting value from the effective configuration."""
        return self.context["settings"].get(setting_name, default)

    def set_setting(self, setting_name: str, value: Any, scope: str) -> None:
        """Set a setting value in the specified scope."""
        config = self.get_config(scope)
        config["settings"][setting_name] = value
        self.save_config(config, scope)
    
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
    
    @staticmethod
    def _deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = AdvancedRTSettings._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result

def get_parameter_value(param_name: str, default: Any = None) -> Any:
    """
    Utility function to get a parameter value from the context.
    
    This function tries to get a parameter value from the context.
    
    Args:
        param_name: The name of the parameter to get
        default: Default value to return if parameter not found
        
    Returns:
        Parameter value from the most appropriate source
    """
    from .context import ContextManager
    
    try:
        # Get context instance
        ctx = ContextManager.get_instance()
        
        # Get parameter value using advanced settings
        return ctx.settings.get_param_value(param_name, default)
    except RuntimeError:
        # No context available
        return default