# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands
- Install: `pip install -e .`
- Run CLI: `cli-tool [COMMAND] [OPTIONS]` or `python -m cli_base.main [COMMAND] [OPTIONS]`
- Run specific test: `python tool_test.py [COMMAND] [OPTIONS]`
- Interactive LLM chat: `cli-tool chat --profile [PROFILE_NAME]`
- Verbose mode: Add `-v` flag to any command for detailed output

## Code Style Guidelines
- Use type hints for all function parameters and return values
- Follow PEP 8 naming conventions (snake_case for functions/variables, CamelCase for classes)
- Group imports: standard library first, then third-party, then local modules
- Use docstrings for all modules, classes, and functions (follow Google docstring format)
- Implement proper error handling with specific exception types
- Use the OutputFormatter class for terminal output (success, info, error, warning)
- For CLI commands, use Click decorators consistently
- Maintain context using ContextManager for settings/state
- Use f-strings for string formatting rather than .format() or %
- Keep methods focused and generally under 50 lines