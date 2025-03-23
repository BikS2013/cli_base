"""
Profile management utilities for CLI tool.
Handles different types of profiles like LLM, database, etc.
"""

import json
from typing import Dict, Any, List, Optional, TypedDict
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