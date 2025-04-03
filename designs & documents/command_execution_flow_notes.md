1. The command starts at the entry point in `cli_base/main.py`. The entry point is the `cli()` function defined in pyproject.toml as `cli-tool = "cli_base.main:cli"`
2. The click.Group (and other click classes) class is initialized
3. Click parses the global options (`--global`, `--local`, `--file`, etc.)
4. Click identifies `generate` as a subcommand of the main CLI
2. The `generate_group` Command Group (from `cli_base/llm/commands.py`) is activated
3. Click identifies `prompt` as a subcommand of `generate`
4. The `generate_prompt` function (from `cli_base/llm/commands.py`) is selected for execution

```
main.py:cli() -> commands.py:generate_group() -> commands.py:generate_prompt()
```

5. `ContextManager` is initialized or retrieved
6. `RTSettings` is initialized with CLI arguments including scope options
7. Configuration files are loaded based on precedence rules
8. The runtime context is built by merging configurations

```
commands.py:generate_prompt() ->
context.py:_initialize_context({scope, file_path}) ->
  context.py:ContextManager.get_instance() or 
  context.py:ContextManager.initialize() ->
    rtsettings.py:RTSettings.__init__() ->
      rtsettings.py:RTSettings._initialize_config_files() ->
      rtsettings.py:RTSettings._load_configurations() ->
      rtsettings.py:RTSettings._build_runtime_context()
```

9. `LLMProfileManager` is created to manage LLM profiles
10. Default profile is retrieved (checking across all scopes if necessary)
11. Profile data is retrieved from configuration
12. The LLM adapter is initialized with the profile data

```
commands.py:generate_prompt() ->
  llm_extension.py:get_llm_profile_manager() ->
    llm_extension.py:LLMProfileManager.__init__() 
  
  profiles.py:ProfileManager.get_default_profile() ->
    rtsettings.py:RTSettings.get_default_profile_from_any_scope()
    
  profiles.py:ProfileManager.get_profile() ->
    rtsettings.py:RTSettings.get_profile_from_any_scope()
    
  llm_extension.py:LLMProfileManager.get_llm() ->
    adapter.py:LLMAdapter.create_llm()
``` 

