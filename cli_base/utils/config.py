"""
Configuration management utility for CLI tool.
Handles global, local, and named configuration files.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union


class ConfigManager:
    """Manages configuration files at global, local, and named levels."""

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

    def __init__(self):
        self.global_config_dir = Path.home() / ".cli-tool"
        self.global_config_path = self.global_config_dir / "config.json"
        self.local_config_dir = Path.cwd() / ".cli-tool"
        self.local_config_path = self.local_config_dir / "config.json"
        
        # Initialize default configuration files if they don't exist
        self._initialize_config_files()

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

    def get_config_path(self, scope: str, file_path: Optional[str] = None) -> Path:
        """Get the path to the configuration file based on scope."""
        if scope == "global":
            return self.global_config_path
        elif scope == "local":
            return self.local_config_path
        elif scope == "file" and file_path:
            return Path(os.path.expanduser(file_path))
        else:
            raise ValueError(f"Invalid scope: {scope}")

    def read_config(self, scope: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Read configuration from the specified scope."""
        config_path = self.get_config_path(scope, file_path)
        
        if not config_path.exists():
            if scope == "local":
                # Create a new local config with default values
                with open(config_path, 'w') as f:
                    json.dump(self.DEFAULT_CONFIG, f, indent=2)
                return self.DEFAULT_CONFIG
            elif scope == "file" and file_path:
                raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file: {config_path}")

    def write_config(self, config: Dict[str, Any], scope: str, file_path: Optional[str] = None) -> None:
        """Write configuration to the specified scope."""
        config_path = self.get_config_path(scope, file_path)
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def update_config(self, updates: Dict[str, Any], scope: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Update configuration with new values, preserving existing structure."""
        config = self.read_config(scope, file_path)
        
        # Helper function to recursively update nested dictionaries
        def update_nested_dict(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    d[k] = update_nested_dict(d[k], v)
                else:
                    d[k] = v
            return d
        
        updated_config = update_nested_dict(config, updates)
        self.write_config(updated_config, scope, file_path)
        return updated_config

    def get_profile(self, profile_type: str, name: str, scope: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific profile from configuration."""
        config = self.read_config(scope, file_path)
        
        if profile_type not in config["profiles"]:
            raise ValueError(f"Profile type not found: {profile_type}")
        
        if name not in config["profiles"][profile_type]:
            raise ValueError(f"Profile not found: {name}")
        
        return config["profiles"][profile_type][name]

    def create_profile(self, profile_type: str, profile: Dict[str, Any], scope: str, file_path: Optional[str] = None) -> None:
        """Create a new profile in the specified configuration."""
        config = self.read_config(scope, file_path)
        
        if profile_type not in config["profiles"]:
            config["profiles"][profile_type] = {}
        
        if profile.get("name") in config["profiles"][profile_type]:
            raise ValueError(f"Profile already exists: {profile.get('name')}")
        
        config["profiles"][profile_type][profile.get("name")] = profile
        self.write_config(config, scope, file_path)

    def list_profiles(self, profile_type: str, scope: str, file_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """List all profiles of a specific type from the configuration."""
        config = self.read_config(scope, file_path)
        
        if profile_type not in config["profiles"]:
            return {}
        
        return config["profiles"][profile_type]

    def edit_profile(self, profile_type: str, name: str, updates: Dict[str, Any], scope: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Edit an existing profile in the configuration."""
        config = self.read_config(scope, file_path)
        
        if profile_type not in config["profiles"]:
            raise ValueError(f"Profile type not found: {profile_type}")
        
        if name not in config["profiles"][profile_type]:
            raise ValueError(f"Profile not found: {name}")
        
        # Update profile
        config["profiles"][profile_type][name].update(updates)
        self.write_config(config, scope, file_path)
        return config["profiles"][profile_type][name]

    def delete_profile(self, profile_type: str, name: str, scope: str, file_path: Optional[str] = None) -> None:
        """Delete a profile from the configuration."""
        config = self.read_config(scope, file_path)
        
        if profile_type not in config["profiles"]:
            raise ValueError(f"Profile type not found: {profile_type}")
        
        if name not in config["profiles"][profile_type]:
            raise ValueError(f"Profile not found: {name}")
        
        # Delete profile
        del config["profiles"][profile_type][name]
        
        # If this was the default profile, clear the default
        if config["defaults"].get(profile_type) == name:
            config["defaults"][profile_type] = None
        
        self.write_config(config, scope, file_path)

    def set_default_profile(self, profile_type: str, name: str, scope: str, file_path: Optional[str] = None) -> None:
        """Set a profile as the default for its type."""
        config = self.read_config(scope, file_path)
        
        if profile_type not in config["profiles"]:
            raise ValueError(f"Profile type not found: {profile_type}")
        
        if name not in config["profiles"][profile_type]:
            raise ValueError(f"Profile not found: {name}")
        
        config["defaults"][profile_type] = name
        self.write_config(config, scope, file_path)

    def get_default_profile(self, profile_type: str, scope: str, file_path: Optional[str] = None) -> Optional[str]:
        """Get the name of the default profile for a type."""
        config = self.read_config(scope, file_path)
        
        if profile_type not in config["defaults"]:
            return None
        
        return config["defaults"].get(profile_type)

    def resolve_effective_config(self) -> Dict[str, Any]:
        """
        Resolve the effective configuration by merging global, local, and file configs
        according to the precedence rules.
        """
        # Start with the global config
        effective_config = self.DEFAULT_CONFIG.copy()
        
        # Try to load and merge global config
        try:
            global_config = self.read_config("global")
            # Merge global config into effective config
            effective_config = self._deep_merge(effective_config, global_config)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Use defaults if global config doesn't exist or is invalid
        
        # Try to load and merge local config
        try:
            local_config = self.read_config("local")
            # Merge local config into effective config
            effective_config = self._deep_merge(effective_config, local_config)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Use previous config if local config doesn't exist or is invalid
        
        return effective_config
    
    @staticmethod
    def _deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result