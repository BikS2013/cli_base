"""
LLM profile command module.
Handles LLM profile management.
"""

import json
import click
from typing import Optional, Dict, Any

from cli_base.commands.cmd_options import json_format_option, json_input_argument, profile_name_option, table_format_option, scope_options
from ..utils.context import ContextManager
from ..utils.formatting import OutputFormatter
from ..utils.context import _initialize_context 
from ..commands.profile_parameter_processor import CreateProfileParameterProcessor, EditProfileParameterProcessor, ProfileParameterProcessor
from ..commands.generic_profile_cmd import (
    create_profile as create_profile,
    list_profiles as list_profiles,
    show_profile as show_profile,
    edit_profile as edit_profile,
    delete_profile as delete_profile,
    use_profile as use_profile
)
from .llm import LLMProfileManager, PROFILE_PARAMS, llm_profile_options

@click.group(name="llm")
def llm_group():
    """Manage LLM profiles."""
    pass

@llm_group.command(name="create")
@llm_profile_options
@scope_options
@json_input_argument
def create(json_input: Optional[str], **kwargs):
    """Create a new LLM profile."""
    # Initialize the LLM manager
    llm_manager = LLMProfileManager()
    create_profile("LLM", llm_manager, json_input, **kwargs)
    
@llm_group.command(name="list")
@scope_options
@table_format_option
def list(scope: str, file_path: Optional[str], output_format: str):
    """List available LLM profiles."""
    # Create LLM profile manager
    llm_manager = LLMProfileManager()
    list_profiles("LLM", llm_manager, PROFILE_PARAMS, scope, file_path, output_format)

@llm_group.command(name="show")
@profile_name_option
@scope_options
@json_format_option
def show(name: str, scope: str, file_path: Optional[str], output_format: str):
    """Show LLM profile details."""
    # Create LLM profile manager
    llm_manager = LLMProfileManager()
    show_profile("LLM", llm_manager, name, scope, file_path, output_format)

@llm_group.command(name="edit")
@profile_name_option
@llm_profile_options
@scope_options
@json_input_argument
def edit(name: str, json_input: Optional[str], **kwargs):
    """Edit an existing LLM profile."""
    llm_manager = LLMProfileManager()
    edit_profile("LLM", llm_manager, name, json_input, **kwargs)

@llm_group.command(name="delete")
@profile_name_option
@scope_options
@click.confirmation_option(prompt="Are you sure you want to delete this profile?")
def delete(name: str, scope: str, file_path: Optional[str]):
    """Delete an LLM profile."""
    # Create LLM profile manager
    llm_manager = LLMProfileManager()
    delete_profile("LLM", llm_manager, name, scope, file_path)

@llm_group.command(name="use")
@profile_name_option
@scope_options
def use(name: str, scope: str, file_path: Optional[str]):
    """Use a specific LLM profile as default."""
    # Create LLM profile manager
    llm_manager = LLMProfileManager()
    use_profile("LLM", llm_manager, name, scope, file_path)
