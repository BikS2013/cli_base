# Universal CLI Tool

A comprehensive command-line interface template that provides standardized support for commands, subcommands, complex configurations, profiles management, multi-level configuration files, and LLM integration via LangChain.

## Features

- Support for commands, subcommands, options/parameters, and flags
- Management of complex dependencies through named profiles
- Configuration handling at global, local, and named file levels
- Flexible configuration file management
- Colorful, readable output
- Comprehensive help and schema documentation
- Unified LLM support through LangChain integration
- Support for multiple LLM providers (OpenAI, Anthropic, Google Gemini, Azure OpenAI, AWS Bedrock, and more)
- Streamlined LLM profile management with environment variable support

## Installation

```
pip install -e .
```

## Usage

The CLI tool follows this general structure:

```
cli-tool [COMMAND] [SUBCOMMAND] [OPTIONS] [FLAGS]
```

### Core Commands

- `config`: Manage configuration files (global, local, named)
- `llm`: Manage LLM profiles
- `schema`: Display command structure as ASCII art
- `help`: Display help information

### Configuration Management

The tool supports three levels of configuration files:

1. **Global**: System-wide settings stored in `~/.cli-tool/config.json`
2. **Local**: Project-specific settings stored in `./.cli-tool/config.json`
3. **Named**: User-specified configuration files at any location

Configuration options can be used with any command:

```bash
# Use global scope with any command
cli-tool [command] [subcommand] --global

# Use local scope with any command (default)
cli-tool [command] [subcommand] --local

# Use named file with any command
cli-tool [command] [subcommand] --file /path/to/config.json
```

Configuration management commands:

```bash
# Show content of the local configuration file
cli-tool config show --local

# Save current parameters to global configuration
cli-tool config save --global

# Import configuration from another file
cli-tool config import --from-file "~/my-configs/special.json" --to-local

# Update configuration with current parameters
cli-tool config update --global '{"settings": {"log_level": "debug"}}'
```

### LLM Profile Management

Create and manage LLM profiles with support for multiple providers through LangChain:

```bash
# Create a new LLM profile
cli-tool llm create --name "gpt4-standard" --provider "openai" --model "gpt-4" --api-key "key123" --temperature 0.7 --global

# Create profiles for other providers
cli-tool llm create --name "claude-3" --provider "anthropic" --model "claude-3-sonnet" --api-key "key456" --temperature 0.7 --global
cli-tool llm create --name "gemini-pro" --provider "google" --model "gemini-pro" --api-key "key789" --project-id "my-project" --global

# List all LLM profiles
cli-tool llm list --global

# Show a specific profile
cli-tool llm show --name "gpt4-standard"

# Set a profile as default
cli-tool llm use --name "gpt4-standard"

# Use profile with provider-specific parameters
cli-tool llm create --name "azure-gpt" --provider "azure" --model "gpt-4" --api-key "key123" --deployment "my-deployment" --base-url "https://example.openai.azure.com" --api-version "2023-05-15" --global
```

The CLI tool will automatically use API keys from environment variables if available (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.).

### Schema and Help

View the command structure and get help:

```bash
# Show schema
cli-tool schema show

# Get detailed help
cli-tool help
cli-tool help config
cli-tool help llm create
```

## Development

This CLI tool is built using:

- [Click](https://click.palletsprojects.com/): For command-line interface creation
- [Rich](https://rich.readthedocs.io/): For colorful terminal output
- [LangChain](https://www.langchain.com/): For unified LLM provider integration
- Python 3.11+

### LangChain Integration

The CLI tool uses LangChain to provide a unified interface for working with multiple LLM providers:

- Supports numerous providers including OpenAI, Anthropic, Google, Azure, AWS Bedrock, Cohere, Mistral AI, and more
- Handles provider-specific nuances and requirements
- Provides structured prompt management, streaming support, and token counting
- Simplifies error handling, retries, and timeouts
- Reduces development effort by abstracting provider-specific implementations

## License

This project is licensed under the MIT License.


## Use it as template for CLI tools 
To use it as template for other CLI tools, you have to fork the repo.
You can perform manually the various changes as are described in the tool?adaptation_guide.md or ask from an LLM to do it. 

If you want to use **Claude Code** you can try the following command: 
``` 
I want you to read the tool_adaptation_guide and follow the instructions to rename the tool from cli-base to
getPage without adding any additional logic.
I don’t want you to install the package at all. 
Just make the changes.
``` 

After the changes have been made you have to run 
```bash 
uv sync 
source .venv/bin/activate
uv pip install -e .
``` 

