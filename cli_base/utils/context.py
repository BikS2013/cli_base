"""
Context management utilities for CLI tool.
Provides access to runtime settings throughout the CLI.
"""

from typing import Optional, Dict, Any
from .rtsettings import RTSettings


class ContextManager:
    """
    Singleton context manager to provide access to runtime settings across the CLI.
    """
    _instance = None
    _settings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContextManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, cli_args: Optional[Dict[str, Any]] = None) -> 'ContextManager':
        """Initialize the context manager with CLI arguments."""
        instance = cls()
        instance._settings = RTSettings(cli_args)
        return instance

    @classmethod
    def get_instance(cls) -> 'ContextManager':
        """Get the singleton instance of the context manager."""
        if cls._instance is None or cls._instance._settings is None:
            raise RuntimeError("ContextManager not initialized. Call initialize() first.")
        return cls._instance

    @property
    def settings(self) -> RTSettings:
        """Get the runtime settings object."""
        if self._settings is None:
            raise RuntimeError("Runtime settings not initialized.")
        return self._settings
    
def _initialize_context(cli_args: Dict[str, Any]) -> ContextManager:
    """
    Initialize or get the context manager instance.
    
    This function checks if the context manager has already been initialized.
    If it has, it will update the context with any new CLI arguments,
    particularly focusing on configuration scope options (--global, --local, --file).
    
    Args:
        cli_args: Command-line arguments passed to the command
        
    Returns:
        The initialized or updated ContextManager instance
    """
    try:
        # Get existing context manager
        ctx = ContextManager.get_instance()
        
        # Update existing context with configuration scope options if provided
        if cli_args:
            current_settings = ctx.settings
            
            # Update file_path option if provided
            if cli_args.get("file_path"):
                current_settings.cli_args["file_path"] = cli_args["file_path"]
                current_settings.named_config_path = None  # Reset to force reload
                current_settings.named_config = None
            
            # Update scope option if provided
            if cli_args.get("scope"):
                current_settings.cli_args["scope"] = cli_args["scope"]
                current_settings.context["current_scope"] = cli_args["scope"]
            
            # Reload configurations and rebuild context with updated settings
            current_settings._load_configurations()
            current_settings._build_runtime_context()
        
        return ctx
    except RuntimeError:
        # Initialize new context manager if not already initialized
        return ContextManager.initialize(cli_args)