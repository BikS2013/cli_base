"""
Parameter resolution utilities for CLI commands.
Handles the retrieval and preparation of all parameters needed for command execution.
"""

import click
from typing import Any, Dict, Optional, List, Callable, TypeVar, Union, Set
import inspect
from .context import ContextManager, _initialize_context
from .rtsettings import RTSettings

# Type variable for the command function
CommandFunc = TypeVar('CommandFunc', bound=Callable)

class ParameterResolver:
    """
    Handles the resolution of parameters for CLI commands.
    
    This class is responsible for retrieving and validating all required parameters
    for command execution from various sources (CLI args, config files, etc.)
    before the actual command execution.
    """
    
    def __init__(self):
        """Initialize a parameter resolver."""
        self._param_cache = {}
    
    def resolve_command_params(self, ctx: click.Context) -> Dict[str, Any]:
        """
        Resolve all parameters for a command based on Click context.
        
        This method extracts all parameters needed for the command including:
        - CLI parameters directly provided by the user
        - Configuration parameters from the appropriate scope
        - Default values from the command definition
        - Environment variables (if supported by the parameter)
        
        Args:
            ctx: Click context containing command and parameter information
            
        Returns:
            A dictionary of resolved parameters, ready to be passed to the command
        """
        # Get the command object from the context
        command = ctx.command
        
        # Initialize parameters with the ones already in the context
        params = dict(ctx.params)
        
        # Process configuration scope options first
        scope_params = self._extract_scope_params(params)
        
        # Initialize or update context manager with scope parameters
        _initialize_context(scope_params)
        
        # Get the effective configuration
        rt_settings = ContextManager.get_instance().settings
        effective_config = rt_settings.get_effective_config()
        
        # Get command-specific parameters from configuration if available
        command_path = self._get_command_path(ctx)
        config_params = self._get_config_params_for_command(effective_config, command_path)
        
        # Merge parameters with configuration values for missing parameters
        for param_name, param_obj in self._get_command_params(command).items():
            # Skip if parameter is already resolved through CLI
            if param_name in params and params[param_name] is not None:
                continue
                
            # Try to get from configuration
            if param_name in config_params and config_params[param_name] is not None:
                params[param_name] = config_params[param_name]
                continue
                
            # Use default value if none provided
            if param_obj.default is not None and param_obj.default != click.types.UnprocessedParamType():
                params[param_name] = param_obj.default
        
        # Process any special parameters (like profiles) that need additional resolution
        params = self._resolve_special_parameters(params, effective_config, command_path)
        
        return params
    
    def _extract_scope_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract configuration scope parameters from all parameters.
        
        Args:
            params: All parameters from Click context
            
        Returns:
            Dictionary containing only the scope-related parameters
        """
        scope_params = {}
        
        # Extract file_path parameter
        if "file_path" in params and params["file_path"] is not None:
            scope_params["file_path"] = params["file_path"]
            
        # Extract scope parameter
        if "scope" in params and params["scope"] is not None:
            scope_params["scope"] = params["scope"]
            
        return scope_params
    
    def _get_command_path(self, ctx: click.Context) -> str:
        """
        Get the full command path for the current command.
        
        Args:
            ctx: Click context
            
        Returns:
            String representation of the command path (e.g., "generate.prompt")
        """
        command_path = []
        current = ctx
        
        # Walk up the context hierarchy to build the full command path
        while current is not None:
            if current.info_name and current.info_name != 'cli':  # Skip the main CLI
                command_path.insert(0, current.info_name)
            current = current.parent
            
        return ".".join(command_path)
    
    def _get_command_params(self, command: Union[click.Command, click.Group]) -> Dict[str, click.Parameter]:
        """
        Get all parameters defined for a command.
        
        Args:
            command: Click command or group object
            
        Returns:
            Dictionary mapping parameter names to parameter objects
        """
        return {param.name: param for param in command.params}
    
    def _get_config_params_for_command(self, config: Dict[str, Any], command_path: str) -> Dict[str, Any]:
        """
        Get command-specific parameters from configuration.
        
        Args:
            config: Effective configuration dictionary
            command_path: Command path string (e.g., "generate.prompt")
            
        Returns:
            Dictionary of parameter values specific to the command
        """
        # If configuration has a commands section with values for this command, use them
        if "commands" in config and command_path in config["commands"]:
            return config["commands"][command_path]
            
        return {}
    
    def _resolve_special_parameters(self, params: Dict[str, Any], 
                                    config: Dict[str, Any], 
                                    command_path: str) -> Dict[str, Any]:
        """
        Resolve special parameters that require additional processing.
        
        Args:
            params: Currently resolved parameters
            config: Effective configuration
            command_path: Command path string
            
        Returns:
            Updated parameters with special values resolved
        """
        # Handle profile parameters if present
        # For example, if a parameter is named "profile" and refers to a profile type
        if "profile" in params and params["profile"] is None:
            # For LLM commands, try to resolve the profile
            if command_path.startswith("generate") or command_path.startswith("llm"):
                default_profile = self._get_default_profile("llm", config)
                if default_profile:
                    params["profile"] = default_profile
        
        return params
    
    def _get_default_profile(self, profile_type: str, config: Dict[str, Any]) -> Optional[str]:
        """
        Get the default profile name for a specific profile type.
        
        Args:
            profile_type: Type of profile (e.g., "llm", "database")
            config: Effective configuration
            
        Returns:
            Default profile name or None if not set
        """
        if "defaults" in config and profile_type in config["defaults"]:
            return config["defaults"][profile_type]
        return None

# Create a decorator that applies parameter resolution to a command
def with_resolved_params(func: CommandFunc) -> CommandFunc:
    """
    Decorator that resolves all parameters for a command before execution.
    
    This decorator wraps a command function to ensure all parameters
    are resolved and validated before the command is executed.
    
    Args:
        func: The command function to wrap
        
    Returns:
        Wrapped function that receives resolved parameters
    """
    def wrapper(*args, **kwargs):
        # Get the current Click context
        ctx = click.get_current_context()
        
        # Resolve parameters
        resolver = ParameterResolver()
        resolved_params = resolver.resolve_command_params(ctx)
        
        # Update kwargs with resolved parameters
        for name, value in resolved_params.items():
            if name not in kwargs or kwargs[name] is None:
                kwargs[name] = value
        
        # Call the original function with resolved parameters
        return func(*args, **kwargs)
    
    # Preserve the original function's metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    
    return wrapper

def resolve_params(ctx: Optional[click.Context] = None) -> Dict[str, Any]:
    """
    Resolve all parameters for the current command.
    
    This utility function can be called directly to get resolved parameters
    without using the decorator.
    
    Args:
        ctx: Click context (if None, the current context will be used)
        
    Returns:
        Dictionary of resolved parameters
    """
    if ctx is None:
        ctx = click.get_current_context()
        
    resolver = ParameterResolver()
    return resolver.resolve_command_params(ctx)