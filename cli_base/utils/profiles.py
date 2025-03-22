"""
Profile management utilities for CLI tool.
Handles different types of profiles like LLM, database, etc.
"""

import json
from typing import Dict, Any, List, Optional
from .config import ConfigManager


class ProfileManager:
    """Manages profiles for different types of dependencies."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    def create_profile(self, profile_type: str, profile_data: Dict[str, Any], scope: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Create a new profile."""
        # Validate profile data (basic validation)
        if not profile_data.get("name"):
            raise ValueError("Profile must have a name")
        
        # Create profile in configuration
        self.config_manager.create_profile(profile_type, profile_data, scope, file_path)
        return profile_data
    
    def list_profiles(self, profile_type: str, scope: str, file_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """List all profiles of a specific type."""
        return self.config_manager.list_profiles(profile_type, scope, file_path)
    
    def get_profile(self, profile_type: str, name: str, scope: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific profile."""
        return self.config_manager.get_profile(profile_type, name, scope, file_path)
    
    def edit_profile(self, profile_type: str, name: str, updates: Dict[str, Any], scope: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Edit an existing profile."""
        return self.config_manager.edit_profile(profile_type, name, updates, scope, file_path)
    
    def delete_profile(self, profile_type: str, name: str, scope: str, file_path: Optional[str] = None) -> None:
        """Delete a profile."""
        self.config_manager.delete_profile(profile_type, name, scope, file_path)
    
    def use_profile(self, profile_type: str, name: str, scope: str, file_path: Optional[str] = None) -> None:
        """Set a profile as the default for its type."""
        self.config_manager.set_default_profile(profile_type, name, scope, file_path)
    
    def parse_profile_input(self, input_str: str) -> Dict[str, Any]:
        """Parse profile input string, which can be JSON or a name reference."""
        try:
            # Try to parse as JSON
            return json.loads(input_str)
        except json.JSONDecodeError:
            # Not valid JSON, assume it's a profile name reference
            return {"name": input_str}


class LLMProfileManager(ProfileManager):
    """Specialized profile manager for LLM profiles."""
    
    LLM_PROFILE_SCHEMA = {
        "name": str,
        "provider": str,
        "model": str,
        "deployment": str,
        "api_key": str,
        "base_url": str,
        "api_version": str,
        "temperature": float
    }
    
    def validate_llm_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validate LLM profile data against schema."""
        # Check required fields
        required_fields = ["name", "provider", "model", "api_key"]
        for field in required_fields:
            if field not in profile:
                raise ValueError(f"Missing required field: {field}")
        
        # Set default values for optional fields
        defaults = {
            "deployment": None,
            "base_url": self._get_default_base_url(profile.get("provider")),
            "api_version": "v1",
            "temperature": 0.7
        }
        
        for field, default_value in defaults.items():
            if field not in profile:
                profile[field] = default_value
        
        # Validate temperature range
        if not 0.0 <= profile.get("temperature", 0.7) <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        
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
    
    def create_profile(self, profile_data: Dict[str, Any], scope: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Create a new LLM profile."""
        profile_data = self.validate_llm_profile(profile_data)
        return super().create_profile("llm", profile_data, scope, file_path)
    
    def list_profiles(self, scope: str, file_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """List all LLM profiles."""
        return super().list_profiles("llm", scope, file_path)
    
    def get_profile(self, name: str, scope: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific LLM profile."""
        return super().get_profile("llm", name, scope, file_path)
    
    def edit_profile(self, name: str, updates: Dict[str, Any], scope: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Edit an existing LLM profile."""
        return super().edit_profile("llm", name, updates, scope, file_path)
    
    def delete_profile(self, name: str, scope: str, file_path: Optional[str] = None) -> None:
        """Delete an LLM profile."""
        super().delete_profile("llm", name, scope, file_path)
    
    def use_profile(self, name: str, scope: str, file_path: Optional[str] = None) -> None:
        """Set an LLM profile as the default."""
        super().use_profile("llm", name, scope, file_path)