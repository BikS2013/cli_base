"""
Model list module for LLM providers.
Provides lists of available models for different LLM providers.
"""

from typing import List, Dict

# Model lists for each provider
OPENAI_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
]

ANTHROPIC_MODELS = [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    "claude-2.1",
    "claude-2.0",
    "claude-instant-1.2",
]

GOOGLE_MODELS = [
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-1.0-pro",
    "gemini-1.0-ultra",
]

AZURE_MODELS = [
    # Azure uses deployment names, but these are the base models
    "gpt-4",
    "gpt-4-turbo",
    "gpt-4-vision",
    "gpt-3.5-turbo",
]

AWS_MODELS = [
    "anthropic.claude-3-opus-20240229",
    "anthropic.claude-3-sonnet-20240229",
    "anthropic.claude-3-haiku-20240307",
    "amazon.titan-text-express-v1",
    "amazon.titan-text-lite-v1",
    "meta.llama3-8b-instruct-v1:0",
    "meta.llama3-70b-instruct-v1:0",
]

COHERE_MODELS = [
    "command",
    "command-r",
    "command-r-plus",
    "command-light",
    "command-nightly",
]

MISTRAL_MODELS = [
    "mistral-large-latest",
    "mistral-medium-latest",
    "mistral-small-latest",
    "mixtral-8x7b-instruct",
]

TOGETHER_MODELS = [
    "togethercomputer/llama-3-8b",
    "togethercomputer/llama-3-70b",
    "togethercomputer/nous-hermes2-mixtral-8x7b",
    "Meta-Llama/Llama-3-70b-chat-hf",
    "Meta-Llama/Llama-3-8b-chat-hf",
]

OLLAMA_MODELS = [
    "llama3",
    "llama3:8b",
    "llama3:70b",
    "mistral",
    "mixtral",
    "gemma",
    "phi3",
    "codellama",
    "llava",
]

# Map of provider to model list
PROVIDER_MODELS: Dict[str, List[str]] = {
    "openai": OPENAI_MODELS,
    "anthropic": ANTHROPIC_MODELS,
    "google": GOOGLE_MODELS,
    "azure": AZURE_MODELS,
    "aws": AWS_MODELS,
    "cohere": COHERE_MODELS,
    "mistral": MISTRAL_MODELS,
    "together": TOGETHER_MODELS,
    "ollama": OLLAMA_MODELS,
    # LiteLLM can use any model from any provider, so don't provide a specific list
    "litellm": [],
}

def get_models_for_provider(provider: str) -> List[str]:
    """
    Get a list of available models for a specific provider.
    
    Args:
        provider: The provider to get models for (e.g., "openai", "anthropic")
        
    Returns:
        A list of model names for the provider
    """
    provider = provider.lower()
    return PROVIDER_MODELS.get(provider, [])