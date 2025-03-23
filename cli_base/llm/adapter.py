"""
LangChain adapter for LLM integration in the CLI tool.
This module translates between CLI profile configuration and LangChain model instances.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Tuple

# Import core LangChain types
from langchain_core.language_models import BaseChatModel

# Set up logging
logger = logging.getLogger(__name__)

class LLMAdapter:
    """Adapter for initializing LangChain LLMs from CLI profiles."""
    
    @classmethod
    def create_llm(cls, profile: Dict[str, Any]) -> BaseChatModel:
        """
        Create a LangChain LLM instance from a profile.
        
        Args:
            profile: LLM profile configuration
            
        Returns:
            A LangChain chat model instance
            
        Raises:
            ValueError: If provider is not supported or required parameters are missing
            ImportError: If required LangChain modules are not installed
        """
        if not profile:
            raise ValueError("Profile cannot be empty")
        
        # Get provider (required)
        provider = profile.get("provider", "").lower()
        if not provider:
            raise ValueError("Provider is required")
        
        # Extract common parameters
        common_params = cls._extract_common_params(profile)
        
        # Handle model_kwargs if present
        if "model_kwargs" in profile and profile["model_kwargs"]:
            try:
                if isinstance(profile["model_kwargs"], str):
                    model_kwargs = json.loads(profile["model_kwargs"])
                else:
                    model_kwargs = profile["model_kwargs"]
                common_params.update(model_kwargs)
            except json.JSONDecodeError as e:
                raise ValueError(f"model_kwargs must be valid JSON: {str(e)}")
        
        # Create provider-specific LLM
        try:
            if provider == "openai":
                return cls._create_openai_llm(profile, common_params)
            
            elif provider == "anthropic":
                return cls._create_anthropic_llm(profile, common_params)
            
            elif provider == "google":
                return cls._create_google_llm(profile, common_params)
            
            elif provider == "azure":
                return cls._create_azure_llm(profile, common_params)
                
            elif provider == "aws":
                return cls._create_aws_llm(profile, common_params)
                
            elif provider == "ollama":
                return cls._create_ollama_llm(profile, common_params)
                
            elif provider == "cohere":
                return cls._create_cohere_llm(profile, common_params)
                
            elif provider == "mistral":
                return cls._create_mistral_llm(profile, common_params)
                
            elif provider == "together":
                return cls._create_together_llm(profile, common_params)
                
            elif provider == "litellm":
                return cls._create_litellm_llm(profile, common_params)
            
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except ImportError as e:
            raise ImportError(f"Missing required package for provider '{provider}'. {str(e)}")
        except Exception as e:
            raise ValueError(f"Error creating LLM for provider '{provider}': {str(e)}")
    
    @staticmethod
    def _extract_common_params(profile: Dict[str, Any]) -> Dict[str, Any]:
        """Extract common parameters from profile."""
        # Basic params
        params = {
            "model": profile.get("model"),
            "temperature": profile.get("temperature", 0.7),
        }
        
        # Only include max_tokens if specified
        if "max_tokens" in profile and profile["max_tokens"] is not None:
            params["max_tokens"] = profile["max_tokens"]
            
        # Add timeout if specified
        if "timeout" in profile and profile["timeout"] is not None:
            params["request_timeout"] = profile["timeout"]
            
        return params
    
    @staticmethod
    def _create_openai_llm(profile: Dict[str, Any], common_params: Dict[str, Any]) -> BaseChatModel:
        """Create OpenAI LLM instance."""
        from langchain_openai import ChatOpenAI
        
        # Extract OpenAI-specific parameters
        openai_params = {
            "api_key": profile.get("api_key"),
            "organization": profile.get("organization"),
        }
        
        # Set base URL if provided
        if "base_url" in profile and profile["base_url"]:
            openai_params["base_url"] = profile["base_url"]
        
        # Combine parameters
        params = {**common_params, **openai_params}
        
        # Create and return the LLM
        return ChatOpenAI(**params)
    
    @staticmethod
    def _create_anthropic_llm(profile: Dict[str, Any], common_params: Dict[str, Any]) -> BaseChatModel:
        """Create Anthropic LLM instance."""
        from langchain_anthropic import ChatAnthropic
        
        # Extract Anthropic-specific parameters
        anthropic_params = {
            "api_key": profile.get("api_key"),
        }
        
        # Set base URL if provided
        if "base_url" in profile and profile["base_url"]:
            anthropic_params["base_url"] = profile["base_url"]
        
        # Combine parameters
        params = {**common_params, **anthropic_params}
        
        # Create and return the LLM
        return ChatAnthropic(**params)
    
    @staticmethod
    def _create_google_llm(profile: Dict[str, Any], common_params: Dict[str, Any]) -> BaseChatModel:
        """Create Google LLM instance."""
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Extract Google-specific parameters
        google_params = {
            "google_api_key": profile.get("api_key"),
        }
        
        # Set project ID if provided
        if "project_id" in profile and profile["project_id"]:
            google_params["project"] = profile["project_id"]
        
        # Combine parameters
        params = {**common_params, **google_params}
        
        # Create and return the LLM
        return ChatGoogleGenerativeAI(**params)
    
    @staticmethod
    def _create_azure_llm(profile: Dict[str, Any], common_params: Dict[str, Any]) -> BaseChatModel:
        """Create Azure OpenAI LLM instance."""
        from langchain_openai import AzureChatOpenAI
        
        # Extract Azure-specific parameters
        azure_params = {
            "api_key": profile.get("api_key"),
            "azure_deployment": profile.get("deployment"),
            "azure_endpoint": profile.get("base_url"),
            "api_version": profile.get("api_version", "2023-05-15"),
        }
        
        # Combine parameters
        params = {**common_params, **azure_params}
        
        # Create and return the LLM
        return AzureChatOpenAI(**params)
    
    @staticmethod
    def _create_aws_llm(profile: Dict[str, Any], common_params: Dict[str, Any]) -> BaseChatModel:
        """Create AWS Bedrock LLM instance."""
        try:
            from langchain_aws import BedrockChat
        except ImportError:
            # Fallback to community implementation if aws package not available
            from langchain_community.chat_models import BedrockChat
        
        # Extract AWS-specific parameters
        aws_params = {
            "region_name": profile.get("region"),
        }
        
        # Set API key if provided (not needed if using environment credentials)
        if "api_key" in profile and profile["api_key"]:
            aws_params["credentials_profile_name"] = profile["api_key"]
        
        # Combine parameters
        params = {**common_params, **aws_params}
        
        # Create and return the LLM
        return BedrockChat(**params)
    
    @staticmethod
    def _create_ollama_llm(profile: Dict[str, Any], common_params: Dict[str, Any]) -> BaseChatModel:
        """Create Ollama LLM instance."""
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            # Fallback to community implementation
            from langchain_community.chat_models import ChatOllama
        
        # Extract Ollama-specific parameters
        ollama_params = {
            "base_url": profile.get("base_url", "http://localhost:11434"),
        }
        
        # Combine parameters
        params = {**common_params, **ollama_params}
        
        # Create and return the LLM
        return ChatOllama(**params)
    
    @staticmethod
    def _create_cohere_llm(profile: Dict[str, Any], common_params: Dict[str, Any]) -> BaseChatModel:
        """Create Cohere LLM instance."""
        try:
            from langchain_cohere import ChatCohere
        except ImportError:
            # Fallback to community implementation
            from langchain_community.chat_models import ChatCohere
        
        # Extract Cohere-specific parameters
        cohere_params = {
            "api_key": profile.get("api_key"),
        }
        
        # Set base URL if provided
        if "base_url" in profile and profile["base_url"]:
            cohere_params["base_url"] = profile["base_url"]
        
        # Combine parameters
        params = {**common_params, **cohere_params}
        
        # Create and return the LLM
        return ChatCohere(**params)
    
    @staticmethod
    def _create_mistral_llm(profile: Dict[str, Any], common_params: Dict[str, Any]) -> BaseChatModel:
        """Create Mistral LLM instance."""
        try:
            from langchain_mistralai import ChatMistralAI
        except ImportError:
            # Fallback to community implementation
            from langchain_community.chat_models import ChatMistralAI
        
        # Extract Mistral-specific parameters
        mistral_params = {
            "mistral_api_key": profile.get("api_key"),
        }
        
        # Set base URL if provided
        if "base_url" in profile and profile["base_url"]:
            mistral_params["endpoint"] = profile["base_url"]
        
        # Combine parameters
        params = {**common_params, **mistral_params}
        
        # Create and return the LLM
        return ChatMistralAI(**params)
    
    @staticmethod
    def _create_together_llm(profile: Dict[str, Any], common_params: Dict[str, Any]) -> BaseChatModel:
        """Create Together AI LLM instance."""
        # Together AI doesn't have a dedicated package yet, so use community or OpenAI-compatible endpoint
        from langchain_openai import ChatOpenAI
        
        # Extract Together-specific parameters
        together_params = {
            "api_key": profile.get("api_key"),
            "base_url": profile.get("base_url", "https://api.together.xyz"),
        }
        
        # Combine parameters
        params = {**common_params, **together_params}
        
        # Create and return the LLM
        return ChatOpenAI(**params)
    
    @staticmethod
    def _create_litellm_llm(profile: Dict[str, Any], common_params: Dict[str, Any]) -> BaseChatModel:
        """Create LiteLLM instance (proxy for multiple providers)."""
        from langchain_openai import ChatOpenAI
        
        # Extract LiteLLM-specific parameters
        litellm_params = {
            "api_key": profile.get("api_key"),
            "base_url": profile.get("base_url", "http://localhost:8000"),
        }
        
        # Combine parameters
        params = {**common_params, **litellm_params}
        
        # Create and return the LLM
        return ChatOpenAI(**params)