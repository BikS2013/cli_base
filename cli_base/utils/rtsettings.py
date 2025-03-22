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
        Build the runtime context by merging configurations according to precedence rules:
        1. Command line arguments
        2. Named configuration (if specified)
        3. Local configuration
        4. Global configuration
        5. Default values
        """
        # Start with defaults
        runtime_config = self.DEFAULT_CONFIG.copy()
        
        # Merge global config
        runtime_config = self._deep_merge(runtime_config, self.global_config)
        
        # Merge local config
        runtime_config = self._deep_merge(runtime_config, self.local_config)
        
        # Merge named config if available
        if self.named_config:
            runtime_config = self._deep_merge(runtime_config, self.named_config)
        
        # Store in context
        self.context = runtime_config
        
        # Add CLI args to context
        self.context["cli_args"] = self.cli_args
        
        # Add current config scope
        if "scope" in self.cli_args:
            self.context["current_scope"] = self.cli_args["scope"]
        elif self.named_config:
            self.context["current_scope"] = "file"
        else:
            self.context["current_scope"] = "local"  # Default to local

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
        """Get the name of the default profile for a specific type."""
        return self.context["defaults"].get(profile_type)

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