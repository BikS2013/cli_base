
from typing import Any, Dict

import click
from ..utils.profiles import ProfileManager

PROFILE_PARAMS = [
    {"name": "name", "type": str, "help": "Profile name", "required": True},
    {"name": "provider", "type": str, "help": "LLM provider (e.g., openai, anthropic)", "required": False},
    {"name": "model", "type": str, "help": "Model name", "required": False},
    {"name": "deployment", "type": str, "help": "Deployment name (for Azure)", "required": False},
    {"name": "api_key", "type": str, "help": "API key", "required": False},
    {"name": "base_url", "type": str, "help": "Base URL for API", "required": False},
    {"name": "api_version", "type": str, "help": "API version", "required": False},
    {"name": "temperature", "type": float, "help": "Temperature (0.0-1.0)", "required": False}
]

# Helper function to add options dynamically
def llm_profile_options(command):
    """Decorator to add profile options to a command."""
    for param in PROFILE_PARAMS:
        command = click.option(
            f"--{param['name']}", 
            type=param['type'], 
            help=param['help'], 
            required=param.get('required', False)   
        )(command)
    return command


class LLMProfileManager(ProfileManager):
    """Specialized profile manager for LLM profiles."""

    def __init__(self):
        """Initialize an LLM profile manager."""
        super().__init__("llm")
    
    def validate_llm_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validate LLM profile data against schema."""
        # Check required fields
        required_fields = [ param["name"] for param in PROFILE_PARAMS if param.get("required", False) ]
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
    

