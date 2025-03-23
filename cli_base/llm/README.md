# LLM Integration for CLI Base

This module provides LangChain-based LLM integration for the CLI Base framework. It supports multiple LLM providers through a consistent interface and offers both profile management and direct interaction with language models.

## Features

- **Multi-Provider Support**: Works with OpenAI, Anthropic, Google, Azure, AWS, Ollama, Cohere, Mistral, Together, and more
- **Profile Management**: Create, edit, and manage LLM profiles with provider-specific validation
- **Environment Variable Support**: Automatically use API keys from environment variables
- **Interactive Chat**: Chat with LLMs through an interactive command-line interface
- **Prompt Generation**: Send one-off prompts to LLMs with real-time streaming responses
- **Sensitive Field Masking**: API keys and other sensitive data are masked in output
- **Extensible Architecture**: Easy to add support for new LLM providers

## Usage

### Managing LLM Profiles

```bash
# Create a profile
cli-tool llm create --name my-openai --provider openai --model gpt-4o --api-key sk-xxxx

# List profiles
cli-tool llm list

# Set default profile
cli-tool llm use my-openai

# Show profile details
cli-tool llm show my-openai

# Edit a profile
cli-tool llm edit my-openai --temperature 0.8

# Delete a profile
cli-tool llm delete my-openai
```

### Using LLMs

```bash
# Send a prompt using the default profile
cli-tool generate prompt "Explain quantum computing in simple terms"

# Use a specific profile
cli-tool generate prompt "Write a Python function to sort a list" --profile my-openai

# Start an interactive chat
cli-tool generate chat

# Use a specific profile for chat
cli-tool generate chat --profile my-anthropic
```

## Supported Providers

The integration supports the following LLM providers:

1. **OpenAI** (`openai`)
   - Models: gpt-4o, gpt-4-turbo, gpt-3.5-turbo, etc.
   - Key parameters: api_key, organization, temperature

2. **Anthropic** (`anthropic`)
   - Models: claude-3-opus, claude-3-sonnet, claude-3-haiku, etc.
   - Key parameters: api_key, temperature, max_tokens

3. **Google Gemini** (`google`)
   - Models: gemini-1.5-pro, gemini-1.5-flash, etc.
   - Key parameters: api_key, project_id, temperature

4. **Microsoft Azure** (`azure`)
   - Models: Based on OpenAI models
   - Key parameters: api_key, deployment, base_url, api_version

5. **AWS Bedrock** (`aws`)
   - Models: anthropic.claude-3, amazon.titan, etc.
   - Key parameters: region, (optional) api_key

6. **Ollama** (`ollama`)
   - Models: llama3, mistral, phi3, etc.
   - Key parameters: base_url

7. **Cohere** (`cohere`)
   - Models: command, command-r, etc.
   - Key parameters: api_key

8. **Mistral AI** (`mistral`)
   - Models: mistral-large-latest, mistral-medium-latest, etc.
   - Key parameters: api_key

9. **Together AI** (`together`)
   - Models: togethercomputer/llama-3-70b, etc.
   - Key parameters: api_key

10. **LiteLLM** (`litellm`)
    - Models: Proxies to other LLM providers
    - Key parameters: base_url, api_key

## Environment Variables

API keys can be loaded from environment variables following this pattern:

```
<PROVIDER>_API_KEY
```

Examples:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `AZURE_API_KEY`
- etc.

## Architecture

The LLM integration consists of:

1. **LLMProfileManager**: Extends BaseProfileManager to handle LLM-specific profile validation and defaults
2. **LLMAdapter**: Translates between CLI profiles and LangChain model instances
3. **commands.py**: Provides CLI commands for interacting with LLMs
4. **model_list.py**: Lists available models for each provider

## Dependencies

Core dependencies:
- langchain-core
- langchain-openai
- langchain-anthropic
- langchain-google-genai

Optional dependencies (installed with `pip install cli-base[llm-all]`):
- langchain-community
- langchain-aws
- langchain-cohere
- langchain-mistralai
- langchain-ollama
- litellm