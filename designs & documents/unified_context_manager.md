# Unified Context Manager Implementation

## Overview

We've merged the standard `ContextManager` and `AdvancedContextManager` classes into a single unified `ContextManager` class. This simplifies the codebase by eliminating duplication and providing a consistent interface regardless of whether advanced settings are being used.

## Changes Made

1. **Merged Context Manager Classes**:
   - Combined functionality from both `ContextManager` and `AdvancedContextManager` into a single class
   - Added a flag to track whether advanced settings are in use
   - Provided a unified interface for accessing settings

2. **Centralized Context Initialization**:
   - Moved `initialize_advanced_context` function to the context.py module
   - Ensured unified error handling and fallback behavior
   - Added type hinting and better documentation

3. **Simplified Parameter Resolution**:
   - Updated the `get_parameter_value` function to work with the unified context manager
   - Improved error handling and parameter resolution flow

4. **Updated Imports and References**:
   - Fixed import statements across the codebase to use the unified context manager
   - Removed deprecated references to `AdvancedContextManager`
   - Streamlined context initialization in command functions

## Implementation Details

### Unified Context Manager

The core of the implementation is the enhanced `ContextManager` class that can handle both standard and advanced settings:

```python
class ContextManager:
    """Singleton context manager to provide access to runtime settings across the CLI."""
    _instance = None
    _settings = None
    _advanced_settings = None
    _using_advanced = False

    @classmethod
    def initialize(cls, cli_args):
        # Initialize with standard settings
        instance = cls()
        instance._settings = RTSettings(cli_args)
        instance._using_advanced = False
        cls._instance = instance
        return instance

    @classmethod
    def initialize_advanced(cls, cli_args, resolver):
        # Initialize with advanced settings
        instance = cls()
        instance._advanced_settings = AdvancedRTSettings(cli_args, resolver)
        instance._using_advanced = True
        cls._instance = instance
        return instance

    @property
    def settings(self):
        # Return the appropriate settings object
        if self._using_advanced and self._advanced_settings is not None:
            return self._advanced_settings
        elif not self._using_advanced and self._settings is not None:
            return self._settings
        else:
            raise RuntimeError("Runtime settings not initialized.")
    
    @property
    def is_using_advanced(self):
        # Check if using advanced settings
        return self._using_advanced
```

### Context Initialization

The `initialize_advanced_context` function now serves as the primary entry point for context initialization:

```python
def initialize_advanced_context(cli_args=None, resolver=None):
    """Initialize or update the context manager with advanced settings."""
    # Try to get existing context or create a new one
    try:
        ctx = ContextManager.get_instance()
        
        # Update settings based on current state
        if ctx.is_using_advanced and cli_args:
            ctx._advanced_settings = AdvancedRTSettings(cli_args, resolver)
        elif not ctx.is_using_advanced:
            ctx = ContextManager.initialize_advanced(cli_args, resolver)
        
        return ctx
    except RuntimeError:
        # Initialize new context with advanced settings
        return ContextManager.initialize_advanced(cli_args, resolver)
```

## Benefits

1. **Simplified Code**: Reduces duplicate code and provides a cleaner interface
2. **Better Maintainability**: Single point of maintenance for context management
3. **Improved Type Safety**: Better type hinting and error handling
4. **Consistent Behavior**: Uniform interface regardless of context type
5. **Reduced Cognitive Load**: Developers only need to understand one context manager API

## Usage Example

```python
# Import necessary components
from cli_base.utils.context import ContextManager, initialize_advanced_context
from cli_base.utils.param_resolver import ParameterResolver

# Initialize with advanced settings
resolver = ParameterResolver()
initialize_advanced_context({"scope": "local"}, resolver=resolver)

# Get context and settings
ctx = ContextManager.get_instance()
settings = ctx.settings

# Check if using advanced settings
if ctx.is_using_advanced:
    # Access advanced-specific features
    param_value = settings.get_param_value("some_param")
else:
    # Use standard settings features
    param_value = settings.cli_args.get("some_param")
```

## Future Improvements

1. **Full Migration**: Complete the migration of all commands to use the unified context manager
2. **Context Convenience Methods**: Add helper methods to the context manager for common operations
3. **Improved Parameter Resolution**: Enhance parameter resolution capabilities
4. **Context State Management**: Add better state management to track context changes
5. **Transition Plan**: Create a plan to fully deprecate the standard settings in favor of advanced settings