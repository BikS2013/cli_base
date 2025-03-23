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
    """Initialize or get the context manager instance."""
    try:
        return ContextManager.get_instance()
    except RuntimeError:
        return ContextManager.initialize(cli_args)