"""
Profile management utilities for CLI tool.
Handles different types of profiles like LLM, database, etc.
"""

import json
from typing import Dict, Any, List, Optional
from .context import ContextManager


class ProfileManager:
    """Manages profiles for different types of dependencies."""
    
    def __init__(self, profile_type: str):
        """
        Initialize a profile manager for a specific profile type.
        
        Args:
            profile_type: The type of profile to manage (e.g., "llm", "database")
        """
        self.profile_type = profile_type
    
    def create_profile(self, profile_data: Dict[str, Any], scope: str) -> Dict[str, Any]:
        """Create a new profile."""
        # Validate profile data (basic validation)
        if not profile_data.get("name"):
            raise ValueError("Profile must have a name")
        
        # Get runtime settings
        rt = ContextManager.get_instance().settings
        
        # Create profile in configuration
        rt.create_profile(self.profile_type, profile_data, scope)
        return profile_data
    
    def list_profiles(self, scope: str) -> Dict[str, Dict[str, Any]]:
        """List all profiles of a specific type."""
        rt = ContextManager.get_instance().settings
        return rt.get_profiles(self.profile_type, scope)
    
    def get_profile(self, name: str) -> Dict[str, Any]:
        """Get a specific profile from the effective configuration."""
        rt = ContextManager.get_instance().settings
        return rt.get_profile(self.profile_type, name)
    
    def get_profile_from_scope(self, name: str, scope: str) -> Dict[str, Any]:
        """Get a specific profile from a specific scope."""
        rt = ContextManager.get_instance().settings
        profiles = rt.get_profiles(self.profile_type, scope)
        
        if name not in profiles:
            raise ValueError(f"Profile not found: {name}")
        
        return profiles[name]
    
    def edit_profile(self, name: str, updates: Dict[str, Any], scope: str) -> Dict[str, Any]:
        """Edit an existing profile."""
        rt = ContextManager.get_instance().settings
        return rt.edit_profile(self.profile_type, name, updates, scope)
    
    def delete_profile(self, name: str, scope: str) -> None:
        """Delete a profile."""
        rt = ContextManager.get_instance().settings
        rt.delete_profile(self.profile_type, name, scope)
    
    def use_profile(self, name: str, scope: str) -> None:
        """Set a profile as the default for its type."""
        rt = ContextManager.get_instance().settings
        rt.set_default_profile(self.profile_type, name, scope)
    
    def get_default_profile(self) -> Optional[str]:
        """Get the name of the default profile."""
        rt = ContextManager.get_instance().settings
        return rt.get_default_profile(self.profile_type)
    
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
    
    def __init__(self):
        """Initialize an LLM profile manager."""
        super().__init__("llm")
    
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
    
    def create_profile(self, profile_data: Dict[str, Any], scope: str) -> Dict[str, Any]:
        """Create a new LLM profile."""
        profile_data = self.validate_llm_profile(profile_data)
        return super().create_profile(profile_data, scope)