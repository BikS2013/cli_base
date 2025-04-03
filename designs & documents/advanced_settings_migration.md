# Advanced Settings Migration

## Overview

This document explains the migration from the dual settings system (RTSettings and AdvancedRTSettings) to a unified settings system that uses only the advanced settings features. This migration simplifies the codebase, reduces duplication, and standardizes how settings and parameters are managed across the application.

## Changes Made

1. **Eliminated Dual Settings System**:
   - Removed the non-advanced settings option entirely
   - Made AdvancedRTSettings the sole settings implementation
   - Unified the context management through a simplified ContextManager class

2. **Simplified Context Management**:
   - Merged ContextManager and AdvancedContextManager into a single class
   - Consolidated initialization logic into a single function
   - Removed conditional code paths for different settings types

3. **Standardized Parameter Resolution**:
   - Made parameter resolution consistently use the advanced approach
   - Ensured all commands benefit from command-specific configurations
   - Simplified the parameter retrieval process

4. **Updated API**:
   - Renamed functions to remove "advanced" prefix
   - Updated function signatures and return types
   - Added better error handling throughout

5. **Removed Legacy Code**:
   - Removed RTSettings class completely
   - Removed duplicate context management logic
   - Kept minimal compatibility functions for backwards compatibility

## Implementation Details

### Context Management

The ContextManager class has been simplified to use only advanced settings:

```python
class ContextManager:
    """Singleton context manager for runtime settings."""
    _instance = None
    _settings = None

    @classmethod
    def initialize(cls, cli_args=None, resolver=None):
        """Initialize with advanced settings."""
        instance = cls()
        instance._settings = AdvancedRTSettings(cli_args, resolver)
        cls._instance = instance
        return instance

    @property
    def settings(self):
        """Get the settings object."""
        if self._settings is None:
            raise RuntimeError("Runtime settings not initialized.")
        return self._settings
```

### Settings Initialization

The initialization process has been standardized:

```python
def initialize_context(cli_args=None, resolver=None):
    """
    Initialize the context manager with settings.
    
    This function serves as the main entry point for initializing
    the context manager.
    """
    # Try to get existing context or create a new one
    try:
        ctx = ContextManager.get_instance()
        # Update settings if args provided
        if cli_args:
            ctx._settings = AdvancedRTSettings(cli_args, resolver)
        return ctx
    except RuntimeError:
        # No context exists, initialize one
        return ContextManager.initialize(cli_args, resolver)
```

### Parameter Resolution

All parameter resolution now uses the advanced approach:

```python
def get_parameter_value(param_name, default=None):
    """Get a parameter value from the context."""
    try:
        ctx = ContextManager.get_instance()
        return ctx.settings.get_param_value(param_name, default)
    except RuntimeError:
        return default
```

## Migration Guide

If you have code that used the old settings system, you can migrate it using these steps:

1. **Replace RTSettings References**:
   - Change any references to `RTSettings` to use `AdvancedRTSettings`
   - Update type hints and import statements

2. **Update Context Initialization**:
   - Replace calls to `_initialize_context()` with `initialize_context()`
   - Replace calls to `initialize_advanced_context()` with `initialize_context()`

3. **Simplify Settings Access**:
   - Use `ctx.settings` instead of checking for different settings types
   - Use `get_parameter_value()` for accessing parameters by name

4. **Remove Advanced Distinctions**:
   - Remove checks for `is_using_advanced`
   - Remove references to `advanced_settings` property

## Benefits

1. **Simplified Code**: One settings system means less code and fewer conditionals
2. **Better Maintainability**: Reduced duplication makes maintenance easier
3. **Consistent Behavior**: All commands work the same way with settings
4. **Enhanced Features**: All commands benefit from advanced parameter resolution
5. **Better Developer Experience**: Clearer API with fewer special cases

## Examples

### Before:

```python
def initialize_settings():
    if use_advanced:
        ctx = initialize_advanced_context(cli_args)
        settings = ctx.advanced_settings
    else:
        ctx = _initialize_context(cli_args)
        settings = ctx.settings
    return settings
```

### After:

```python
def initialize_settings():
    ctx = initialize_context(cli_args)
    settings = ctx.settings
    return settings
```

## Conclusion

The migration to a unified settings system simplifies the codebase while enhancing its capabilities. By standardizing on the more powerful advanced settings implementation, we've eliminated redundancy and improved the overall architecture of the application.