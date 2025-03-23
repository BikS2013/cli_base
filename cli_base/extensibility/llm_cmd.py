"""
LLM profile command module.
Handles LLM profile management.
"""

import json
import click
from typing import Optional, Dict, Any
from ..utils.context import ContextManager
from ..utils.formatting import OutputFormatter
from ..utils.context import _initialize_context 
from ..commands.profile_parameter_processor import CreateProfileParameterProcessor, EditProfileParameterProcessor, ProfileParameterProcessor
from ..commands.generic_profile_cmd import (
    create_profile as generic_create_profile,
    list_profiles as generic_list_profiles,
    show_profile as generic_show_profile,
    edit_profile as generic_edit_profile,
    delete_profile as generic_delete_profile,
    use_profile as generic_use_profile
)
from .llm import LLMProfileManager, PROFILE_PARAMS, llm_profile_options

@click.group(name="llm")
def llm_group():
    """Manage LLM profiles."""
    pass

@llm_group.command(name="create")
@llm_profile_options
@click.option("--global", "scope", flag_value="global", help="Use global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Use local configuration.")
@click.option("--file", "file_path", type=str, help="Use named configuration file.")
@click.argument("json_input", required=False)
def create_profile(json_input: Optional[str], **kwargs):
    """Create a new LLM profile."""
    # Initialize the LLM manager
    llm_manager = LLMProfileManager()
    generic_create_profile("LLM", llm_manager, json_input, **kwargs)
    
@llm_group.command(name="list")
@click.option("--global", "scope", flag_value="global", help="List from global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="List from local configuration.")
@click.option("--file", "file_path", type=str, help="List from named configuration file.")
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="table", help="Output format")
def list_profiles(scope: str, file_path: Optional[str], output_format: str):
    """List available LLM profiles."""
    # Create LLM profile manager
    llm_manager = LLMProfileManager()
    generic_list_profiles("LLM", llm_manager, PROFILE_PARAMS, scope, file_path, output_format)

@llm_group.command(name="show")
@click.option("--name", type=str, required=True, help="Profile name")
@click.option("--global", "scope", flag_value="global", help="Show from global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Show from local configuration.")
@click.option("--file", "file_path", type=str, help="Show from named configuration file.")
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="json", help="Output format")
def show_profile(name: str, scope: str, file_path: Optional[str], output_format: str):
    """Show LLM profile details."""
    # Create LLM profile manager
    llm_manager = LLMProfileManager()
    generic_show_profile("LLM", llm_manager, name, scope, file_path, output_format)

@llm_group.command(name="edit")
@click.option("--name", type=str, required=True, help="Profile name")
@llm_profile_options
@click.option("--global", "scope", flag_value="global", help="Edit in global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Edit in local configuration.")
@click.option("--file", "file_path", type=str, help="Edit in named configuration file.")
@click.argument("json_input", required=False)
def edit_profile(name: str, json_input: Optional[str], **kwargs):
    """Edit an existing LLM profile."""
    llm_manager = LLMProfileManager()
    generic_edit_profile("LLM", llm_manager, name, json_input, **kwargs)

@llm_group.command(name="delete")
@click.option("--name", type=str, required=True, help="Profile name")
@click.option("--global", "scope", flag_value="global", help="Delete from global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Delete from local configuration.")
@click.option("--file", "file_path", type=str, help="Delete from named configuration file.")
@click.confirmation_option(prompt="Are you sure you want to delete this profile?")
def delete_profile(name: str, scope: str, file_path: Optional[str]):
    """Delete an LLM profile."""
    # Create LLM profile manager
    llm_manager = LLMProfileManager()
    generic_delete_profile("LLM", llm_manager, name, scope, file_path)

@llm_group.command(name="use")
@click.option("--name", type=str, required=True, help="Profile name")
@click.option("--global", "scope", flag_value="global", help="Set as default in global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Set as default in local configuration.")
@click.option("--file", "file_path", type=str, help="Set as default in named configuration file.")
def use_profile(name: str, scope: str, file_path: Optional[str]):
    """Use a specific LLM profile as default."""
    # Create LLM profile manager
    llm_manager = LLMProfileManager()
    generic_use_profile("LLM", llm_manager, name, scope, file_path)
