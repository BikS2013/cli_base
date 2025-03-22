"""
Configuration command module.
Handles configuration file operations.
"""

import json
import click
from typing import Optional, Dict, Any
from ..utils.context import ContextManager
from ..utils.formatting import OutputFormatter


@click.group(name="config")
def config_group():
    """Manage configuration files (global, local, named)."""
    pass


@config_group.command(name="show")
@click.option("--global", "scope", flag_value="global", help="Use global configuration.")
@click.option("--local", "scope", flag_value="local", help="Use local configuration.")
@click.option("--file", "file_path", type=str, help="Use named configuration file.")
def show_config(scope: str, file_path: Optional[str] = None):
    """Display configuration content."""
    # Update context with command-specific arguments
    ctx = ContextManager.get_instance()
    rt = ctx.settings
    
    # Validate scope + file_path combination
    if scope is None and file_path is None:
        scope = "local"  # Default to local if not specified
    elif scope is None and file_path is not None:
        scope = "file"
    
    try:
        # Get configuration based on scope
        config = rt.get_config(scope)
        OutputFormatter.print_json(config, f"{scope.capitalize()} Configuration")
    except (FileNotFoundError, ValueError) as e:
        OutputFormatter.print_error(str(e))


@config_group.command(name="save")
@click.option("--global", "scope", flag_value="global", help="Use global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Use local configuration.")
@click.option("--file", "file_path", type=str, help="Use named configuration file.")
def save_config(scope: str, file_path: Optional[str] = None):
    """Save current parameters to configuration."""
    # Get runtime settings
    ctx = ContextManager.get_instance()
    rt = ctx.settings
    
    # For demonstration, we're just using the default config
    # In a real implementation, this would use current parameters from context
    try:
        rt.save_config(rt.DEFAULT_CONFIG, scope)
        OutputFormatter.print_success(f"Configuration saved to {scope} config.")
    except (ValueError, IOError) as e:
        OutputFormatter.print_error(str(e))


@config_group.command(name="update")
@click.option("--global", "scope", flag_value="global", help="Use global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Use local configuration.")
@click.option("--file", "file_path", type=str, help="Use named configuration file.")
@click.argument("update_json", required=True)
def update_config(scope: str, update_json: str, file_path: Optional[str] = None):
    """Update configuration with current parameters."""
    # Get runtime settings
    ctx = ContextManager.get_instance()
    rt = ctx.settings
    
    try:
        # Parse update JSON
        updates = json.loads(update_json)
        
        # Validate scope + file_path combination
        if scope is None and file_path is not None:
            scope = "file"
        
        # Update config
        rt.update_config(updates, scope)
        OutputFormatter.print_success(f"Configuration updated in {scope} config.")
    except json.JSONDecodeError:
        OutputFormatter.print_error("Invalid JSON format for update.")
    except (ValueError, IOError) as e:
        OutputFormatter.print_error(str(e))


@config_group.command(name="replace")
@click.option("--global", "scope", flag_value="global", help="Use global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Use local configuration.")
@click.option("--file", "file_path", type=str, help="Use named configuration file.")
@click.argument("config_json", required=True)
def replace_config(scope: str, config_json: str, file_path: Optional[str] = None):
    """Replace entire configuration with current parameters."""
    # Get runtime settings
    ctx = ContextManager.get_instance()
    rt = ctx.settings
    
    try:
        # Parse replacement JSON
        new_config = json.loads(config_json)
        
        # Validate scope + file_path combination
        if scope is None and file_path is not None:
            scope = "file"
        
        # Replace config
        rt.save_config(new_config, scope)
        OutputFormatter.print_success(f"Configuration replaced in {scope} config.")
    except json.JSONDecodeError:
        OutputFormatter.print_error("Invalid JSON format for configuration.")
    except (ValueError, IOError) as e:
        OutputFormatter.print_error(str(e))


@config_group.command(name="import")
@click.option("--from-global", "from_scope", flag_value="global", help="Import from global configuration.")
@click.option("--from-local", "from_scope", flag_value="local", help="Import from local configuration.")
@click.option("--from-file", "from_file", type=str, help="Import from named configuration file.")
@click.option("--to-global", "to_scope", flag_value="global", help="Import to global configuration.")
@click.option("--to-local", "to_scope", flag_value="local", help="Import to local configuration.")
@click.option("--to-file", "to_file", type=str, help="Import to named configuration file.")
@click.option("--replace", is_flag=True, help="Replace entire configuration instead of merging.")
def import_config(from_scope: str, from_file: Optional[str], to_scope: str, to_file: Optional[str], replace: bool):
    """Import configuration from another file."""
    # Get runtime settings
    ctx = ContextManager.get_instance()
    rt = ctx.settings
    
    try:
        # Determine source and destination configurations
        if from_scope is None and from_file is None:
            raise ValueError("Must specify a source configuration (--from-global, --from-local, or --from-file).")
        
        if to_scope is None and to_file is None:
            raise ValueError("Must specify a destination configuration (--to-global, --to-local, or --to-file).")
        
        # Set up CLI args for source
        if from_file:
            # Initialize a temporary RTSettings for the from-file
            temp_settings = ContextManager.initialize({"file_path": from_file})
            source_scope = "file"
            source_config = temp_settings.settings.get_config("file")
        else:
            source_scope = from_scope
            source_config = rt.get_config(source_scope)
        
        # Set up destination 
        if to_file:
            # Update the temporary settings for the to-file
            temp_settings = ContextManager.initialize({"file_path": to_file})
            dest_scope = "file"
            
            if replace:
                # Replace destination with source
                temp_settings.settings.save_config(source_config, dest_scope)
            else:
                # Merge source into destination
                try:
                    dest_config = temp_settings.settings.get_config(dest_scope)
                    merged_config = rt._deep_merge(dest_config, source_config)
                    temp_settings.settings.save_config(merged_config, dest_scope)
                except FileNotFoundError:
                    # If destination file doesn't exist, create it with source config
                    temp_settings.settings.save_config(source_config, dest_scope)
        else:
            dest_scope = to_scope
            
            if replace:
                # Replace destination with source
                rt.save_config(source_config, dest_scope)
            else:
                # Merge source into destination
                dest_config = rt.get_config(dest_scope)
                merged_config = rt._deep_merge(dest_config, source_config)
                rt.save_config(merged_config, dest_scope)
        
        OutputFormatter.print_success("Configuration imported successfully.")
    except (ValueError, IOError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))


@config_group.command(name="export")
@click.option("--from-global", "from_scope", flag_value="global", help="Export from global configuration.")
@click.option("--from-local", "from_scope", flag_value="local", help="Export from local configuration.")
@click.option("--from-file", "from_file", type=str, help="Export from named configuration file.")
@click.option("--to-file", "to_file", type=str, required=True, help="Export to named configuration file.")
def export_config(from_scope: str, from_file: Optional[str], to_file: str):
    """Export configuration to another file."""
    # Get runtime settings
    ctx = ContextManager.get_instance()
    rt = ctx.settings
    
    try:
        # Determine source configuration
        if from_scope is None and from_file is None:
            from_scope = "local"  # Default to local if not specified
        
        # Load source configuration
        if from_file:
            # Initialize a temporary RTSettings for the from-file
            temp_settings = ContextManager.initialize({"file_path": from_file})
            source_config = temp_settings.settings.get_config("file")
        else:
            source_config = rt.get_config(from_scope)
        
        # Write to destination file
        with open(to_file, 'w') as f:
            json.dump(source_config, f, indent=2)
        
        OutputFormatter.print_success(f"Configuration exported to {to_file}.")
    except (ValueError, IOError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))


@config_group.command(name="reset")
@click.option("--global", "scope", flag_value="global", help="Reset global configuration.")
@click.option("--local", "scope", flag_value="local", help="Reset local configuration.")
@click.option("--file", "file_path", type=str, help="Reset named configuration file.")
@click.confirmation_option(prompt="Are you sure you want to reset the configuration?")
def reset_config(scope: str, file_path: Optional[str] = None):
    """Reset configuration to defaults."""
    # Get runtime settings
    ctx = ContextManager.get_instance()
    rt = ctx.settings
    
    try:
        # Validate scope + file_path combination
        if scope is None and file_path is None:
            scope = "local"  # Default to local if not specified
        elif scope is None and file_path is not None:
            scope = "file"
        
        # Reset config to defaults
        rt.save_config(rt.DEFAULT_CONFIG, scope)
        OutputFormatter.print_success(f"{scope.capitalize()} configuration reset to defaults.")
    except (ValueError, IOError) as e:
        OutputFormatter.print_error(str(e))


@config_group.command(name="generate")
@click.option("--global", "scope", flag_value="global", help="Generate from global configuration.")
@click.option("--local", "scope", flag_value="local", help="Generate from local configuration.")
@click.option("--file", "file_path", type=str, help="Generate from named configuration file.")
def generate_config(scope: str, file_path: Optional[str] = None):
    """Generate command-line instructions based on configuration."""
    # Get runtime settings
    ctx = ContextManager.get_instance()
    rt = ctx.settings
    
    try:
        # Validate scope + file_path combination
        if scope is None and file_path is None:
            scope = "local"  # Default to local if not specified
        elif scope is None and file_path is not None:
            scope = "file"
        
        # Read configuration
        config = rt.get_config(scope)
        
        # Generate command-line instructions for LLM profiles
        if "profiles" in config and "llm" in config["profiles"]:
            for name, profile in config["profiles"]["llm"].items():
                cmd = f"cli-tool llm create --name \"{name}\""
                
                for key, value in profile.items():
                    if key != "name":
                        cmd += f" --{key.replace('_', '-')} \"{value}\""
                
                cmd += f" --{scope}"
                
                click.echo(cmd)
        
        # Generate additional commands based on configuration...
        # (This would be expanded in a real implementation)
        
    except (ValueError, IOError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))