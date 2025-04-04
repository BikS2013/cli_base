# Command Execution Flow

This document explains the step-by-step execution flow when running a command like `cli-tool ask "why is the sky blue?"`. It details which classes and objects are created and activated, and the sequence of method calls during command execution.

## Execution Flow Overview

When you run a CLI command, the following high-level flow occurs:

1. CLI entry point initialization
2. Command parsing and routing
3. Configuration loading and context setup
4. Command execution
5. Result formatting and display

## Detailed Flow for `ask` Command

### 1. Entry Point Initialization

```
cli-tool ask "why is the sky blue?"
```

1. The command starts at the entry point in `cli_base/main.py`
2. The `cli()` function is called by Click's command line parser
3. Click parses the global options (`--global`, `--local`, `--file`, etc.)

**Classes Initialized:**
- `click.Group` from the Click library for the main CLI

**Method Sequence:**
```
main.py:cli() -> [Click initialization]
```

### 2. Command Parsing and Routing

1. Click identifies `ask` as a command of the main CLI
2. The `ask_command` Command (from `cli_base/llm/commands.py`) is activated

**Classes Activated:**
- `click.Command` for the `ask` command

**Method Sequence:**
```
main.py:cli() -> commands.py:ask_command()
```

### 3. Configuration Loading and Context Setup

1. `ContextManager` is initialized or retrieved
2. `RTSettings` is initialized with CLI arguments including scope options
3. Configuration files are loaded based on precedence rules
4. The runtime context is built by merging configurations

**Classes and Objects Created:**
- `ContextManager` singleton (from `cli_base/utils/context.py`)
- `RTSettings` (from `cli_base/utils/advanced_settings.py`)
- `ConfigManager` (from `cli_base/utils/config.py`) used internally by RTSettings

**Method Sequence:**
```
commands.py:ask_command() ->
context.py:initialize_context({scope, file_path}) ->
  context.py:ContextManager.initialize() ->
    advanced_settings.py:AdvancedRTSettings.__init__() ->
      advanced_settings.py:AdvancedRTSettings._initialize_config_files() ->
      advanced_settings.py:AdvancedRTSettings._load_configurations() ->
      advanced_settings.py:AdvancedRTSettings._build_runtime_context()
```

### 4. LLM Profile Management

1. `LLMProfileManager` is created to manage LLM profiles
2. Default profile is retrieved (checking across all scopes if necessary)
3. Profile data is retrieved from configuration
4. The LLM adapter is initialized with the profile data

**Classes and Objects Created:**
- `LLMProfileManager` (from `cli_base/extensibility/llm_extension.py`)
- `BaseProfileManager` (parent class from `cli_base/utils/profiles.py`)
- `ProfileManager` (base parent class from `cli_base/utils/profiles.py`)
- `LLMAdapter` (from `cli_base/llm/adapter.py`)

**Method Sequence:**
```
commands.py:ask_command() ->
  llm_extension.py:get_llm_profile_manager() ->
    llm_extension.py:LLMProfileManager.__init__() 
  
  profiles.py:ProfileManager.get_default_profile() ->
    advanced_settings.py:AdvancedRTSettings.get_default_profile_from_any_scope()
    
  profiles.py:ProfileManager.get_profile() ->
    advanced_settings.py:AdvancedRTSettings.get_profile_from_any_scope()
    
  llm_extension.py:LLMProfileManager.get_llm() ->
    adapter.py:LLMAdapter.create_llm()
```

### 5. LangChain Integration and Execution

1. LangChain model is created based on the profile configuration
2. The prompt is converted to a LangChain message
3. The model is invoked or streamed to generate a response
4. The response is formatted and displayed

**Classes and Objects Created:**
- `LangChain` chat model (varies based on provider: OpenAI, Anthropic, etc.)
- `HumanMessage` for prompt representation (from `langchain_core.messages`)

**Method Sequence:**
```
commands.py:ask_command() ->
  adapter.py:LLMAdapter.create_llm() ->
    [LangChain specific model creation] ->
  
  # For streaming output:
  llm.stream([HumanMessage(content=prompt)]) ->
    [Output chunks displayed]
    
  # For complete output:
  llm.invoke([HumanMessage(content=prompt)]) ->
    [Complete output displayed]
```

## Configuration Loading Details

A critical part of command execution is loading the appropriate configuration based on scope options:

### Configuration Loading Sequence

1. Default configuration is loaded first
2. Global configuration (`~/.cli-tool/config.json`) is loaded and merged
3. Local configuration (`./.cli-tool/config.json`) is loaded and merged, if using `--local` or default
4. Custom file configuration is loaded and merged, if using `--file`

**Method Sequence for Configuration Loading:**
```
advanced_settings.py:AdvancedRTSettings._load_configurations() ->
  [Load global config] ->
  [Load local config] ->
  [Load file config if specified]

advanced_settings.py:AdvancedRTSettings._build_runtime_context() ->
  [Deep merge configurations based on precedence rules]
```

## Profile Resolution Flow

When retrieving a profile (like an LLM profile), the system follows these steps:

1. Check if profile exists in the effective merged configuration
2. If not found and using `--file`, check the local configuration
3. If still not found, check the global configuration
4. If not found in any scope, raise an error with helpful information

**Method Sequence for Profile Resolution:**
```
profiles.py:ProfileManager.get_profile() ->
  advanced_settings.py:AdvancedRTSettings.get_profile_from_any_scope() ->
    [Try effective config] ->
    [Try local config if using --file] ->
    [Try global config] ->
    [Raise error if not found]
```

## Error Handling Flow

If a profile cannot be found or there's an error during execution:

1. Error message is displayed using `OutputFormatter`
2. Available profiles from all scopes are listed
3. Helper messages suggest how to create or set default profiles

**Method Sequence for Error Handling:**
```
commands.py:ask_command() ->
  [Try to get profile] ->
  [Exception caught] ->
    OutputFormatter.print_error() ->
    [List profiles from each scope] ->
    OutputFormatter.print_info() # Display helper messages
```

## Complete Object Activation Sequence

The complete sequence of classes being activated and objects being created during the execution of `cli-tool ask "why is the sky blue?"` is:

1. `click.Group` (main CLI)
2. `click.Command` (ask command)
3. `ContextManager` (singleton)
4. `AdvancedRTSettings`
5. `ConfigManager`
6. `LLMProfileManager`
7. `LLMAdapter`
8. LangChain chat model (provider-specific)
9. `HumanMessage`
10. `OutputFormatter` (for results or errors)

This sequence ensures that configuration is properly loaded, the correct profile is identified, and the LLM is initialized with the appropriate settings before processing the prompt and displaying the result.