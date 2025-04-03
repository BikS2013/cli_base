# cli_base/extensibility/llm_extension.py
import os
from typing import Any, Dict, List, Optional

from cli_base.utils.profiles import BaseProfileManager, ProfileValidationResult
from cli_base.extensibility.generator import ProfileCommandGenerator

# Define enhanced profile parameters with LangChain integration
PROFILE_PARAMS = [
    # Core parameters
    {"name": "name", "type": str, "help": "Profile name", "required": True},
    {"name": "provider", "type": str, "help": "LLM provider", "required": True},
    {"name": "model", "type": str, "help": "Model name", "required": True},
    {"name": "api_key", "type": str, "help": "API key", "required": True, "sensitive": True},
    
    # Common LLM parameters
    {"name": "temperature", "type": float, "help": "Temperature (0.0-1.0)", "required": False},
    {"name": "max_tokens", "type": int, "help": "Maximum tokens to generate", "required": False},
    
    # Additional configuration
    {"name": "base_url", "type": str, "help": "Base URL for API (required for some providers)", "required": False},
    {"name": "model_kwargs", "type": str, "help": "Additional model parameters as JSON", "required": False},
    
    # Provider-specific parameters
    {"name": "deployment", "type": str, "help": "Deployment name (for Azure)", "required": False},
    {"name": "api_version", "type": str, "help": "API version", "required": False},
    {"name": "organization", "type": str, "help": "Organization ID (for OpenAI)", "required": False},
    {"name": "region", "type": str, "help": "Cloud region (for Google, AWS)", "required": False},
    {"name": "project_id", "type": str, "help": "Project ID (for Google)", "required": False},
    {"name": "timeout", "type": int, "help": "Request timeout in seconds", "required": False},
]

class LLMProfileManager(BaseProfileManager):
    """Specialized profile manager for LLM profiles with LangChain integration."""

    def __init__(self):
        """Initialize an LLM profile manager."""
        super().__init__("llm", PROFILE_PARAMS)
    
    def _validate_field_values(self, profile: Dict[str, Any]) -> ProfileValidationResult:
        """Validate LLM-specific field values using LangChain."""
        errors = []
        
        # Validate temperature range if specified
        if "temperature" in profile:
            temp = profile["temperature"]
            if not 0.0 <= temp <= 1.0:
                errors.append("Temperature must be between 0.0 and 1.0")
        
        # Validate max_tokens if specified
        if "max_tokens" in profile:
            max_tokens = profile["max_tokens"]
            if max_tokens <= 0:
                errors.append("Max tokens must be greater than 0")
        
        # Validate provider
        if "provider" in profile:
            provider = profile["provider"]
            valid_providers = [
                "openai", "anthropic", "google", "azure", "aws", 
                "ollama", "litellm", "cohere", "mistral", "together"
            ]
            if provider not in valid_providers:
                errors.append(f"Provider must be one of: {', '.join(valid_providers)}")
        
        # Provider-specific validation
        if "provider" in profile and "model" in profile:
            provider_errors = self._validate_provider_specific(profile)
            errors.extend(provider_errors)
        
        # Try to create LangChain model to validate configuration if all required fields are present
        # Only attempt this if we have required fields and no basic validation errors
        if len(errors) == 0 and self._has_required_fields(profile):
            try:
                # Only create model if api_key is present or can be loaded from env
                if "api_key" in profile or self._can_load_api_key_from_env(profile):
                    # Import here to avoid circular imports
                    try:
                        from cli_base.llm.adapter import LLMAdapter
                        # Validation only - we don't need to keep the model
                        LLMAdapter.create_llm(profile)
                    except Exception as e:
                        errors.append(f"LangChain validation error: {str(e)}")
            except ImportError:
                # LangChain not installed, skip this validation
                pass
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "profile": profile
        }
    
    def _validate_provider_specific(self, profile: Dict[str, Any]) -> List[str]:
        """Provider-specific validation logic."""
        provider = profile["provider"]
        errors = []
        
        # Each provider has specific requirements
        if provider == "azure" and "deployment" not in profile:
            errors.append("Azure provider requires a deployment name")
        
        elif provider == "aws" and "region" not in profile:
            errors.append("AWS provider requires a region")
        
        elif provider == "google" and "project_id" not in profile:
            errors.append("Google provider requires a project_id")
        
        # Validate model_kwargs if present
        if "model_kwargs" in profile and profile["model_kwargs"]:
            try:
                import json
                if isinstance(profile["model_kwargs"], str):
                    json.loads(profile["model_kwargs"])
            except json.JSONDecodeError:
                errors.append("model_kwargs must be valid JSON")
        
        return errors
    
    def _has_required_fields(self, profile: Dict[str, Any]) -> bool:
        """Check if profile has minimum required fields for LangChain validation."""
        required = ["provider", "model"]
        return all(field in profile for field in required)
    
    def _can_load_api_key_from_env(self, profile: Dict[str, Any]) -> bool:
        """Check if API key can be loaded from environment variables."""
        if "provider" not in profile:
            return False
            
        provider = profile["provider"].upper()
        env_var = f"{provider}_API_KEY"
        return env_var in os.environ
    
    def _apply_default_values(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values for LLM profiles."""
        provider = profile.get("provider", "")
        
        # Common defaults
        defaults = {
            "temperature": 0.7,
            "max_tokens": 2048,
        }
        
        # Provider-specific defaults
        provider_defaults = {
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "api_version": "v1",
            },
            "anthropic": {
                "base_url": "https://api.anthropic.com/v1",
                "api_version": "v1",
                "max_tokens": 4096,
            },
            "google": {
                "base_url": "https://generativelanguage.googleapis.com",
                "api_version": "v1beta",
            },
            "azure": {
                "api_version": "2023-05-15",
            },
            "aws": {},
            "ollama": {
                "base_url": "http://localhost:11434",
            },
            "litellm": {
                "base_url": "http://localhost:8000",
            },
            "cohere": {
                "base_url": "https://api.cohere.ai",
                "api_version": "v1",
            },
            "mistral": {
                "base_url": "https://api.mistral.ai",
                "api_version": "v1",
            },
            "together": {
                "base_url": "https://api.together.xyz",
                "api_version": "v1",
            }
        }
        
        # Apply provider-specific defaults
        if provider in provider_defaults:
            provider_specific = provider_defaults[provider]
            for field, default_value in provider_specific.items():
                if field not in defaults or defaults[field] is None:
                    defaults[field] = default_value
        
        # Apply defaults to profile
        for field, default_value in defaults.items():
            if field not in profile:
                profile[field] = default_value
        
        # Check for environment variables for API keys
        if "api_key" not in profile or not profile["api_key"]:
            env_var = f"{provider.upper()}_API_KEY"
            if env_var in os.environ:
                profile["api_key"] = os.environ[env_var]
        
        return profile
    
    def get_llm(self, profile_name: str = None) -> Any:
        """
        Get a LangChain LLM instance from a profile.
        
        This method will search for the profile across all configuration scopes
        following the precedence rules.
        
        Args:
            profile_name: Name of the profile to use. If None, uses the default profile.
            
        Returns:
            A LangChain chat model instance
            
        Raises:
            ValueError: If profile not found or no default profile set
            ImportError: If LangChain is not installed
        """
        # Get default profile if none specified
        if profile_name is None:
            profile_name = self.get_default_profile()
            if not profile_name:
                raise ValueError("No default LLM profile set in any configuration scope")
        
        # Get profile data
        try:
            profile = self.get_profile(profile_name)
            
            # Create LLM instance
            try:
                from cli_base.llm.adapter import LLMAdapter
                return LLMAdapter.create_llm(profile)
            except ImportError as e:
                raise ImportError(f"LangChain not installed. Please install LangChain to use this feature: {str(e)}")
        except ValueError as e:
            # Re-raise with a more helpful message
            raise ValueError(f"LLM profile '{profile_name}' not found in any configuration scope. Use 'cli-tool llm list' to see available profiles, or create one with 'cli-tool llm create'.")

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