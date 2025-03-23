# LangChain Integration for LLM Platform Support

## Introduction

This document outlines how to integrate LangChain into the CLI tool to simplify support for multiple LLM platforms. LangChain is a framework designed to enable the development of applications using Large Language Models (LLMs), providing abstractions for model interaction, prompt management, and service integrations.

## Benefits of LangChain Integration

1. **Unified Provider Interface**
   - Abstract away provider-specific implementations
   - Consistent API across all supported LLM platforms
   - Simplified onboarding of new LLM providers

2. **Built-in Support for Multiple Providers**
   - OpenAI, Anthropic, Google Gemini, Azure OpenAI
   - AWS Bedrock, Cohere, Mistral AI, Together AI
   - Local models via Ollama and other self-hosted solutions

3. **Advanced Features**
   - Structured prompt management
   - Streaming support
   - Token counting and cost estimation
   - Consistent error handling
   - Retries and timeouts

4. **Reduced Development Effort**
   - Less provider-specific code to maintain
   - Provider-specific nuances handled by LangChain
   - Focus on CLI experience rather than API integrations

## Implementation Approach

### 1. Enhanced Profile Schema

The profile schema can be streamlined while maintaining provider-specific flexibility:

```python
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
    
    # Provider-specific parameters (only needed for certain providers)
    {"name": "deployment", "type": str, "help": "Deployment name (for Azure)", "required": False},
    {"name": "api_version", "type": str, "help": "API version", "required": False},
    {"name": "organization", "type": str, "help": "Organization ID (for OpenAI)", "required": False},
    {"name": "region", "type": str, "help": "Cloud region (for Google, AWS)", "required": False},
    {"name": "project_id", "type": str, "help": "Project ID (for Google)", "required": False},
]
```

### 2. LangChain Adapter

Create a LangChain adapter layer that translates between the CLI's profile format and LangChain's model initialization:

```python
from typing import Dict, Any, Optional
from langchain_core.language_models import LLM, ChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
# Import other providers as needed

class LLMAdapter:
    """Adapter for initializing LangChain LLMs from CLI profiles."""
    
    @staticmethod
    def create_llm(profile: Dict[str, Any]) -> Optional[ChatModel]:
        """Create a LangChain LLM instance from a profile."""
        provider = profile.get("provider", "").lower()
        
        # Common parameters
        common_params = {
            "model": profile.get("model"),
            "temperature": profile.get("temperature", 0.7),
            "max_tokens": profile.get("max_tokens"),
        }
        
        # Handle model_kwargs if present
        if "model_kwargs" in profile and profile["model_kwargs"]:
            try:
                import json
                model_kwargs = json.loads(profile["model_kwargs"])
                common_params.update(model_kwargs)
            except json.JSONDecodeError:
                raise ValueError("model_kwargs must be valid JSON")
        
        # Create provider-specific LLM
        if provider == "openai":
            return ChatOpenAI(
                api_key=profile.get("api_key"),
                organization=profile.get("organization"),
                base_url=profile.get("base_url"),
                **common_params
            )
        
        elif provider == "anthropic":
            return ChatAnthropic(
                api_key=profile.get("api_key"),
                base_url=profile.get("base_url"),
                **common_params
            )
        
        elif provider == "google":
            return ChatGoogleGenerativeAI(
                api_key=profile.get("api_key"),
                project=profile.get("project_id"),
                **common_params
            )
        
        elif provider == "azure":
            from langchain_openai import AzureChatOpenAI
            return AzureChatOpenAI(
                api_key=profile.get("api_key"),
                azure_deployment=profile.get("deployment"),
                azure_endpoint=profile.get("base_url"),
                api_version=profile.get("api_version", "2023-05-15"),
                **common_params
            )
        
        # Add other providers as needed
        
        raise ValueError(f"Unsupported provider: {provider}")
```

### 3. Enhanced LLMProfileManager

Extend the current `LLMProfileManager` to leverage LangChain's validation capabilities:

```python
import os
from typing import Dict, Any, List
from langchain_core.language_models import ChatModel
from cli_base.utils.profiles import BaseProfileManager, ProfileValidationResult

class LLMProfileManager(BaseProfileManager):
    """Profile manager for LLM profiles with LangChain integration."""
    
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
        
        # Try to create LangChain model to validate configuration
        if len(errors) == 0:
            try:
                # Only validate if all required fields are present
                required_fields = ["provider", "model"]
                if all(field in profile for field in required_fields):
                    from cli_base.llm.adapter import LLMAdapter
                    # Only create model if api_key is present or can be loaded from env
                    if "api_key" in profile or self._can_load_api_key_from_env(profile):
                        LLMAdapter.create_llm(profile)
            except Exception as e:
                errors.append(f"LangChain validation error: {str(e)}")
        
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
        
        return errors
    
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
            },
            "anthropic": {
                "base_url": "https://api.anthropic.com/v1",
                "max_tokens": 4096,
            },
            # Add other provider defaults
        }
        
        # Apply provider-specific defaults
        if provider in provider_defaults:
            defaults.update(provider_defaults[provider])
        
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
    
    def get_llm(self, profile_name: str = None) -> ChatModel:
        """Get a LangChain LLM instance from a profile."""
        # Get default profile if none specified
        if profile_name is None:
            profile_name = self.get_default_profile()
            if not profile_name:
                raise ValueError("No default LLM profile set")
        
        # Get profile data
        profile = self.get_profile(profile_name)
        if not profile:
            raise ValueError(f"LLM profile not found: {profile_name}")
        
        # Create LLM instance
        from cli_base.llm.adapter import LLMAdapter
        return LLMAdapter.create_llm(profile)
```

### 4. Package Dependencies

Add LangChain and provider-specific packages to the project dependencies:

```python
# In pyproject.toml or setup.py
dependencies = [
    # Existing dependencies
    
    # LangChain core
    "langchain-core>=0.1.0",
    
    # Provider-specific packages - can be optional
    "langchain-openai>=0.0.5",  # OpenAI and Azure
    "langchain-anthropic>=0.1.1",
    "langchain-google-genai>=0.0.6",
    # Add others as needed
]
```

## Example Usage

Once integrated, the CLI could offer a smoother experience for LLM interactions:

```python
# In a CLI command that uses LLMs
def generate_command(prompt, profile_name=None):
    # Get LLM profile manager
    profile_manager = LLMProfileManager()
    
    # Get LLM from profile
    llm = profile_manager.get_llm(profile_name)
    
    # Generate response
    from langchain_core.messages import HumanMessage
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Print response
    OutputFormatter.print_success(response.content)
```

## Implementation Roadmap

1. **Add Dependencies**
   - Add LangChain core and provider-specific packages
   - Update installation documentation

2. **Create Basic Structure**
   - Create the LLM adapter module
   - Update profile schema to include LangChain-specific fields

3. **Enhance Profile Manager**
   - Update validation for LangChain compatibility
   - Implement environment variable support
   - Add helper methods for LLM creation

4. **Testing**
   - Unit tests for adapter layer
   - Integration tests with mock API responses
   - End-to-end tests with actual API calls (if possible)

5. **Documentation**
   - Update user documentation for LangChain integration
   - Provide examples for common use cases

## Potential Challenges and Considerations

1. **Dependency Management**
   - LangChain has numerous provider-specific packages
   - Consider making provider packages optional

2. **Version Compatibility**
   - LangChain evolves rapidly
   - Need strategy for handling breaking changes

3. **Performance**
   - Additional abstraction layer may impact performance
   - Consider lightweight options for basic use cases

4. **Caching**
   - Implement result caching for repeated LLM calls
   - Support LangChain's built-in caching mechanisms

5. **Extensibility**
   - Ensure custom providers can be added
   - Allow advanced configuration beyond basic parameters

## Conclusion

Integrating LangChain into the CLI tool will significantly simplify supporting multiple LLM platforms while providing advanced features like structured output parsing, prompt management, and streaming. The adapter-based approach maintains the existing architecture while leveraging LangChain's capabilities.

This integration will make it easier for users to work with different LLM providers through a consistent interface, reducing the maintenance burden of supporting each provider separately while expanding the tool's capabilities.