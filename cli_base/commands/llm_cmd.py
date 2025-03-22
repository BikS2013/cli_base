"""
LLM profile command module.
Handles LLM profile management.
"""

import json
import click
from typing import Optional, Dict, Any
from ..utils.config import ConfigManager
from ..utils.profiles import LLMProfileManager
from ..utils.formatting import OutputFormatter


@click.group(name="llm")
def llm_group():
    """Manage LLM profiles."""
    pass


@llm_group.command(name="create")
@click.option("--name", type=str, help="Profile name")
@click.option("--provider", type=str, help="LLM provider (e.g., openai, anthropic)")
@click.option("--model", type=str, help="Model name")
@click.option("--deployment", type=str, help="Deployment name (for Azure)")
@click.option("--api-key", type=str, help="API key")
@click.option("--base-url", type=str, help="Base URL for API")
@click.option("--api-version", type=str, help="API version")
@click.option("--temperature", type=float, help="Temperature (0.0-1.0)")
@click.option("--global", "scope", flag_value="global", help="Use global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Use local configuration.")
@click.option("--file", "file_path", type=str, help="Use named configuration file.")
@click.argument("json_input", required=False)
def create_profile(
    name: Optional[str],
    provider: Optional[str],
    model: Optional[str],
    deployment: Optional[str],
    api_key: Optional[str],
    base_url: Optional[str],
    api_version: Optional[str],
    temperature: Optional[float],
    scope: str,
    file_path: Optional[str],
    json_input: Optional[str]
):
    """Create a new LLM profile."""
    config_manager = ConfigManager()
    llm_manager = LLMProfileManager(config_manager)
    
    try:
        # Process JSON input if provided
        if json_input:
            profile_data = json.loads(json_input)
        else:
            # Build profile from individual options
            profile_data = {
                "name": name,
                "provider": provider,
                "model": model,
                "api_key": api_key
            }
            
            # Add optional fields if provided
            if deployment:
                profile_data["deployment"] = deployment
            if base_url:
                profile_data["base_url"] = base_url
            if api_version:
                profile_data["api_version"] = api_version
            if temperature is not None:
                profile_data["temperature"] = temperature
        
        # Validate scope + file_path combination
        if scope is None and file_path is not None:
            scope = "file"
        
        # Create profile
        created_profile = llm_manager.create_profile(profile_data, scope, file_path)
        OutputFormatter.print_success(f"LLM profile '{created_profile['name']}' created successfully.")
        OutputFormatter.print_json(created_profile, "Profile Details")
    except (ValueError, json.JSONDecodeError) as e:
        OutputFormatter.print_error(str(e))


@llm_group.command(name="list")
@click.option("--global", "scope", flag_value="global", help="List from global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="List from local configuration.")
@click.option("--file", "file_path", type=str, help="List from named configuration file.")
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="table", help="Output format")
def list_profiles(scope: str, file_path: Optional[str], output_format: str):
    """List available LLM profiles."""
    config_manager = ConfigManager()
    llm_manager = LLMProfileManager(config_manager)
    
    try:
        # Validate scope + file_path combination
        if scope is None and file_path is not None:
            scope = "file"
        
        # List profiles
        profiles = llm_manager.list_profiles(scope, file_path)
        
        if not profiles:
            OutputFormatter.print_info(f"No LLM profiles found in {scope} configuration.")
            return
        
        # Get default profile
        default_profile = config_manager.get_default_profile("llm", scope, file_path)
        
        # Format output
        if output_format == "json":
            OutputFormatter.print_json(profiles, "LLM Profiles")
        else:  # table format
            # Prepare data for table
            table_data = []
            for name, profile in profiles.items():
                row = {
                    "Name": name,
                    "Provider": profile.get("provider", ""),
                    "Model": profile.get("model", ""),
                    "Temperature": profile.get("temperature", ""),
                    "Default": "✓" if name == default_profile else ""
                }
                table_data.append(row)
            
            # Display table
            OutputFormatter.print_table(
                table_data,
                ["Name", "Provider", "Model", "Temperature", "Default"],
                f"LLM Profiles ({scope})"
            )
    except (ValueError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))


@llm_group.command(name="show")
@click.option("--name", type=str, required=True, help="Profile name")
@click.option("--global", "scope", flag_value="global", help="Show from global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Show from local configuration.")
@click.option("--file", "file_path", type=str, help="Show from named configuration file.")
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="json", help="Output format")
def show_profile(name: str, scope: str, file_path: Optional[str], output_format: str):
    """Show LLM profile details."""
    config_manager = ConfigManager()
    llm_manager = LLMProfileManager(config_manager)
    
    try:
        # Validate scope + file_path combination
        if scope is None and file_path is not None:
            scope = "file"
        
        # Get profile
        profile = llm_manager.get_profile(name, scope, file_path)
        
        # Format output
        if output_format == "json":
            OutputFormatter.print_json(profile, f"LLM Profile: {name}")
        else:  # table format
            # Prepare data for table
            table_data = [{
                "Property": key,
                "Value": str(value)
            } for key, value in profile.items()]
            
            # Display table
            OutputFormatter.print_table(
                table_data,
                ["Property", "Value"],
                f"LLM Profile: {name}"
            )
    except (ValueError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))


@llm_group.command(name="edit")
@click.option("--name", type=str, required=True, help="Profile name")
@click.option("--provider", type=str, help="LLM provider")
@click.option("--model", type=str, help="Model name")
@click.option("--deployment", type=str, help="Deployment name")
@click.option("--api-key", type=str, help="API key")
@click.option("--base-url", type=str, help="Base URL for API")
@click.option("--api-version", type=str, help="API version")
@click.option("--temperature", type=float, help="Temperature (0.0-1.0)")
@click.option("--global", "scope", flag_value="global", help="Edit in global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Edit in local configuration.")
@click.option("--file", "file_path", type=str, help="Edit in named configuration file.")
@click.argument("json_input", required=False)
def edit_profile(
    name: str,
    provider: Optional[str],
    model: Optional[str],
    deployment: Optional[str],
    api_key: Optional[str],
    base_url: Optional[str],
    api_version: Optional[str],
    temperature: Optional[float],
    scope: str,
    file_path: Optional[str],
    json_input: Optional[str]
):
    """Edit an existing LLM profile."""
    config_manager = ConfigManager()
    llm_manager = LLMProfileManager(config_manager)
    
    try:
        # Process JSON input if provided
        if json_input:
            updates = json.loads(json_input)
            # Ensure name is preserved if already in the JSON
            if "name" not in updates:
                updates["name"] = name
        else:
            # Build updates from individual options
            updates = {"name": name}
            
            # Add fields if provided
            if provider:
                updates["provider"] = provider
            if model:
                updates["model"] = model
            if deployment:
                updates["deployment"] = deployment
            if api_key:
                updates["api_key"] = api_key
            if base_url:
                updates["base_url"] = base_url
            if api_version:
                updates["api_version"] = api_version
            if temperature is not None:
                updates["temperature"] = temperature
        
        # Validate scope + file_path combination
        if scope is None and file_path is not None:
            scope = "file"
        
        # Edit profile
        updated_profile = llm_manager.edit_profile(name, updates, scope, file_path)
        OutputFormatter.print_success(f"LLM profile '{name}' updated successfully.")
        OutputFormatter.print_json(updated_profile, "Updated Profile")
    except (ValueError, json.JSONDecodeError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))


@llm_group.command(name="delete")
@click.option("--name", type=str, required=True, help="Profile name")
@click.option("--global", "scope", flag_value="global", help="Delete from global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Delete from local configuration.")
@click.option("--file", "file_path", type=str, help="Delete from named configuration file.")
@click.confirmation_option(prompt="Are you sure you want to delete this profile?")
def delete_profile(name: str, scope: str, file_path: Optional[str]):
    """Delete an LLM profile."""
    config_manager = ConfigManager()
    llm_manager = LLMProfileManager(config_manager)
    
    try:
        # Validate scope + file_path combination
        if scope is None and file_path is not None:
            scope = "file"
        
        # Delete profile
        llm_manager.delete_profile(name, scope, file_path)
        OutputFormatter.print_success(f"LLM profile '{name}' deleted successfully.")
    except (ValueError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))


@llm_group.command(name="use")
@click.option("--name", type=str, required=True, help="Profile name")
@click.option("--global", "scope", flag_value="global", help="Set as default in global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Set as default in local configuration.")
@click.option("--file", "file_path", type=str, help="Set as default in named configuration file.")
def use_profile(name: str, scope: str, file_path: Optional[str]):
    """Use a specific LLM profile as default."""
    config_manager = ConfigManager()
    llm_manager = LLMProfileManager(config_manager)
    
    try:
        # Validate scope + file_path combination
        if scope is None and file_path is not None:
            scope = "file"
        
        # Set as default profile
        llm_manager.use_profile(name, scope, file_path)
        OutputFormatter.print_success(f"LLM profile '{name}' set as default in {scope} configuration.")
    except (ValueError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))