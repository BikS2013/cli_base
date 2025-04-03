"""
Context management utilities for CLI tool.
Provides access to runtime settings throughout the CLI.
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

# Import only types to avoid circular imports
if TYPE_CHECKING:
    from .advanced_settings import AdvancedRTSettings
    from .param_resolver import ParameterResolver

class ContextManager:
    """
    Singleton context manager to provide access to runtime settings across the CLI.
    
    This class handles all the runtime settings for the CLI application,
    using the advanced settings system exclusively.
    """
    _instance = None
    _settings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContextManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, cli_args: Optional[Dict[str, Any]] = None,
                   resolver: Optional['ParameterResolver'] = None) -> 'ContextManager':
        """
        Initialize the context manager with advanced settings.
        
        Args:
            cli_args: Command-line arguments
            resolver: Optional parameter resolver
            
        Returns:
            The initialized context manager instance
        """
        from .advanced_settings import AdvancedRTSettings
        
        # Make sure cli_args is at least an empty dict if None
        if cli_args is None:
            cli_args = {}
            
        instance = cls()
        instance._settings = AdvancedRTSettings(cli_args, resolver)
        cls._instance = instance
        return instance

    @classmethod
    def get_instance(cls) -> 'ContextManager':
        """
        Get the singleton instance of the context manager.
        
        Returns:
            The singleton context manager instance
        
        Raises:
            RuntimeError: If the context manager has not been initialized
        """
        if cls._instance is None:
            raise RuntimeError("ContextManager not initialized. Call initialize() first.")
        return cls._instance

    @property
    def settings(self) -> 'AdvancedRTSettings':
        """
        Get the advanced runtime settings object.
        
        Returns:
            The advanced runtime settings object
            
        Raises:
            RuntimeError: If settings are not initialized
        """
        if self._settings is None:
            raise RuntimeError("Runtime settings not initialized.")
        return self._settings

# Main initialization function for the context manager with advanced settings
def initialize_context(cli_args: Optional[Dict[str, Any]] = None,
                      resolver: Optional['ParameterResolver'] = None) -> ContextManager:
    """
    Initialize or update the context manager with advanced settings.
    
    This function serves as the main entry point for initializing
    the context manager.
    
    Args:
        cli_args: Optional command-line arguments
        resolver: Optional parameter resolver
        
    Returns:
        The initialized context manager instance
    """
    # Make sure cli_args is at least an empty dict if None
    if cli_args is None:
        cli_args = {}
    
    try:
        # Try to get existing context manager
        ctx = ContextManager.get_instance()
        
        # Update with new args if provided
        if cli_args:
            from .advanced_settings import AdvancedRTSettings
            ctx._settings = AdvancedRTSettings(cli_args, resolver)
        
        return ctx
    except RuntimeError:
        # No context manager exists, initialize one
        try:
            return ContextManager.initialize(cli_args, resolver)
        except Exception as e:
            # In case of error during initialization, provide fallback behavior
            from .formatting import OutputFormatter
            OutputFormatter.print_error(f"Warning: Error initializing context: {str(e)}")
            
            # Create a basic instance
            from .advanced_settings import AdvancedRTSettings
            instance = ContextManager()
            instance._settings = AdvancedRTSettings(cli_args, resolver)
            ContextManager._instance = instance
            return instance

