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

    