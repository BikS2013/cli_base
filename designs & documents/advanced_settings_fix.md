# Advanced Settings Migration Fix

## Issues Fixed

1. **AttributeError in Parameter Resolver**:
   - Fixed the issue where the parameter resolver was incorrectly using the AdvancedContextManager object instead of a Click context
   - Added safety checks in `_get_command_path` to ensure we're dealing with a proper Click context
   - Stored and preserved the original Click context in `resolve_command_params`
   - Added type checking and attribute validation to prevent attribute errors

2. **Context Initialization Flow**:
   - Added better error handling in parameter resolution
   - Added safety checks to prevent attribute errors
   - Ensured variable naming is consistent to prevent context variable shadowing
   - Improved the initialization process to handle cases where context might not be properly initialized

3. **Config Command Update**:
   - Updated the `show_config` command to use the advanced settings system
   - Added proper parameter resolution using the `@with_resolved_params` decorator
   - Added fallback to regular settings if advanced settings are not available

4. **Advanced Context Manager Enhancements**:
   - Added better error handling in `initialize_advanced_context`
   - Ensured `cli_args` is always at least an empty dict
   - Added fallback behavior when initialization fails
   - Added a wrapper for `ContextManager.get_instance` that tries advanced first, then falls back to regular

5. **LLM Command Updates**:
   - Added proper error handling for context initialization in LLM commands
   - Passed scope parameters to `initialize_advanced_context` in both prompt and chat commands

## Current State

The basic command flow with the advanced settings system now works properly. We've verified that:

1. The `--help` command works correctly
2. The `config show --local` command works and displays the correct configuration
3. The parameter resolver correctly handles the Click context
4. Context initialization is more robust with proper fallbacks
5. Safety checks prevent attribute errors when attributes don't exist
6. Better error handling throughout the advanced settings system

The system now properly falls back to standard settings when advanced settings can't be used, ensuring backward compatibility.

## Update: Unified Context Manager

After implementing the initial fixes, we've further improved the codebase by unifying the context management system:

1. **Merged Context Managers**: Combined `ContextManager` and `AdvancedContextManager` into a single unified class
2. **Simplified API**: Provided a single consistent interface for accessing settings
3. **Improved Type Safety**: Added better type hinting and error handling throughout
4. **Centralized Initialization**: Moved all context initialization logic to the context.py module
5. **Reduced Code Duplication**: Eliminated redundant code and simplified the architecture

See the [unified_context_manager.md](./unified_context_manager.md) document for detailed information about this change.

## Remaining Work

While the core functionality is now working, there are a few items to complete:

1. Update the remaining config_cmd functions to use the `@with_resolved_params` decorator
2. Add more robust error handling for LLM profile management
3. Complete thorough testing of all commands with various flag combinations
4. Add comprehensive unit tests for the advanced settings system
5. Create detailed documentation for how to use the advanced settings system in new commands

## How to Use Advanced Settings

The advanced settings system is now enabled by default in the tool_test.py script. To use it:

```python
# Import the necessary functions
from cli_base.main import cli, initialize_with_advanced_settings

# Enable advanced settings
initialize_with_advanced_settings()

# Run the CLI with arguments
cli(sys.argv[1:])
```

This will enable command-specific configurations, better parameter resolution, and enhanced context management for all commands.