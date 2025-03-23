# cli_base/extensibility/llm.py
from typing import Any, Dict

from cli_base.utils.profiles import BaseProfileManager, ProfileValidationResult
from cli_base.extensibility.generator import ProfileCommandGenerator

# Define profile parameters
PROFILE_PARAMS = [
    {"name": "name", "type": str, "help": "Profile name", "required": True},
    {"name": "provider", "type": str, "help": "LLM provider (e.g., openai, anthropic)", "required": True},
    {"name": "model", "type": str, "help": "Model name", "required": True},
    {"name": "deployment", "type": str, "help": "Deployment name (for Azure)", "required": False},
    {"name": "api_key", "type": str, "help": "API key", "required": True},
    {"name": "base_url", "type": str, "help": "Base URL for API", "required": False},
    {"name": "api_version", "type": str, "help": "API version", "required": False},
    {"name": "temperature", "type": float, "help": "Temperature (0.0-1.0)", "required": False}
]

class LLMProfileManager(BaseProfileManager):
    """Specialized profile manager for LLM profiles."""

    def __init__(self):
        """Initialize an LLM profile manager."""
        super().__init__("llm", PROFILE_PARAMS)
    
    def _validate_field_values(self, profile: Dict[str, Any]) -> ProfileValidationResult:
        """Validate LLM-specific field values."""
        errors = []
        
        # Validate temperature range if specified
        if "temperature" in profile:
            temp = profile["temperature"]
            if not 0.0 <= temp <= 1.0:
                errors.append("Temperature must be between 0.0 and 1.0")
        
        # Validate provider
        if "provider" in profile:
            provider = profile["provider"]
            valid_providers = ["openai", "anthropic", "azure", "cohere"]
            if provider not in valid_providers:
                errors.append(f"Provider must be one of: {', '.join(valid_providers)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "profile": profile
        }
    
    def _apply_default_values(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values for LLM profiles."""
        defaults = {
            "deployment": None,
            "base_url": self._get_default_base_url(profile.get("provider")),
            "api_version": "v1",
            "temperature": 0.7
        }
        
        for field, default_value in defaults.items():
            if field not in profile:
                profile[field] = default_value
                
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

# Create a factory function for the profile manager
def get_llm_profile_manager() -> LLMProfileManager:
    """Factory function to create an LLM profile manager."""
    return LLMProfileManager()

# Create a command generator
llm_command_generator = ProfileCommandGenerator(
    name="LLM",
    command_name="llm",
    description="Manage LLM (Large Language Model) profiles.",
    profile_params=PROFILE_PARAMS,
    profile_manager_factory=get_llm_profile_manager,
    help_texts={
        "create": "Create a new LLM profile with provider, model, and API key settings.",
        "list": "List all available LLM profiles.",
        "show": "Show details for a specific LLM profile.",
        "edit": "Edit an existing LLM profile.",
        "delete": "Delete an LLM profile.",
        "use": "Set a specific LLM profile as the default."
    }
)

# Generate the command group
llm_group = llm_command_generator.generate_command_group()