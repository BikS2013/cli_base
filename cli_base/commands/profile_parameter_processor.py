
import json
from typing import Any, Dict, Optional


class ProfileParameterProcessor:
    """Base class for processing profile parameters."""
    
    @staticmethod
    def resolve_scope(scope: str, file_path: Optional[str]) -> str:
        """Validate and normalize scope parameter."""
        if scope is None and file_path is not None:
            return "file"
        return scope or "local"  # Default to local
    
    @staticmethod
    def process_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate generic parameters."""
        # Basic validation
        if not params.get("name"):
            raise ValueError("Profile name is required")
        return params


class CreateProfileParameterProcessor(ProfileParameterProcessor):
    """Process parameters for profile creation."""
    
    @classmethod
    def from_args(cls, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process parameters from command-line arguments."""
        # Get the keys from the args parameter
        keys = args.keys()
        profile_data = {}
        for key in keys:
            if args.get(key):
                profile_data[key] = args.get(key)
            
        return cls.process_params(profile_data)
    
    @classmethod
    def from_json(cls, json_str: str) -> Dict[str, Any]:
        """Process parameters from JSON input."""
        try:
            profile_data = json.loads(json_str)
            return cls.process_params(profile_data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
        
class EditProfileParameterProcessor(ProfileParameterProcessor):
    """Process parameters for profile editing."""
    
    @classmethod
    def from_args(cls, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process parameters from command-line arguments."""
        # Filter out None values to only update provided fields
        updates = {k: v for k, v in args.items() if v is not None}
        
        # Ensure name is included
        if "name" not in updates:
            raise ValueError("Profile name is required for editing")
            
        return cls.process_params(updates)
    
    @classmethod
    def from_json(cls, json_str: str, profile_name: str) -> Dict[str, Any]:
        """Process parameters from JSON input with a required profile name."""
        try:
            updates = json.loads(json_str)
            
            # Ensure name is preserved if already in the JSON
            if "name" not in updates:
                updates["name"] = profile_name
                
            return cls.process_params(updates)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")