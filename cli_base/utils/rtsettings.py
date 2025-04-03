"""
Runtime settings class for CLI tool.
Centralizes all configuration and parameter management into a cohesive runtime context.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union


class RTSettings:
    """
    Runtime settings class that combines command-line parameters and configuration file settings
    into a unified runtime context for the CLI tool.
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
        }
    }

    def __init__(self, cli_args: Optional[Dict[str, Any]] = None):
        """
        Initialize runtime settings with command-line arguments and load configuration files.
        
        Args:
            cli_args: Command-line arguments passed to the CLI tool
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
        
        # Store CLI arguments
        self.cli_args = cli_args or {}
        
        # Verbose and quiet flags from CLI
        self.verbose = self.cli_args.get("verbose", False)
        self.quiet = self.cli_args.get("quiet", False)
        
        # Runtime context for commands
        self.context = {}
        
        # Initialize configuration files and load settings
        self._initialize_config_files()
        self._load_configurations()
        self._build_runtime_context()

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
        
        # Determine current scope
        current_scope = self.cli_args.get("scope", "local")
        has_file_option = self.cli_args.get("file_path") is not None
        
        # Build config according to specified scope
        if has_file_option:
            # --file option: file -> local -> global -> defaults
            if self.named_config:
                runtime_config = self._deep_merge(runtime_config, self.global_config)
                runtime_config = self._deep_merge(runtime_config, self.local_config)
                runtime_config = self._deep_merge(runtime_config, self.named_config)
                self.context = runtime_config
                self.context["current_scope"] = "file"
            else:
                # If named config not found, fall back to standard precedence
                runtime_config = self._deep_merge(runtime_config, self.global_config)
                runtime_config = self._deep_merge(runtime_config, self.local_config)
                self.context = runtime_config
                self.context["current_scope"] = "local"
        elif current_scope == "global":
            # --global option: only global -> defaults
            runtime_config = self._deep_merge(runtime_config, self.global_config)
            self.context = runtime_config
            self.context["current_scope"] = "global"
        else:
            # --local option or default: local -> global -> defaults
            runtime_config = self._deep_merge(runtime_config, self.global_config)
            runtime_config = self._deep_merge(runtime_config, self.local_config)
            self.context = runtime_config
            self.context["current_scope"] = "local"
        
        # Add CLI args to context
        self.context["cli_args"] = self.cli_args

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

    @staticmethod
    def _deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = RTSettings._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result