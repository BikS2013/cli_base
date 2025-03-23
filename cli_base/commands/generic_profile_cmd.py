import json
from typing import Any, List, Optional

from cli_base.commands.profile_parameter_processor import (
    CreateProfileParameterProcessor,
    EditProfileParameterProcessor, 
    ProfileParameterProcessor
)
from cli_base.utils.context import _initialize_context
from cli_base.utils.formatting import OutputFormatter
from cli_base.utils.profiles import ProfileManager

def extract_scope_params(**kwargs) -> tuple[str,dict[str,Any]]:
    """Extract scope parameters from keyword arguments."""
    # Extract scope parameters
    scope_params = {
        "scope": kwargs.pop("scope", None),
        "file_path": kwargs.pop("file_path", None)
    }

    # Normalize scope
    scope = ProfileParameterProcessor.resolve_scope(
        scope_params["scope"], scope_params["file_path"]
    )

    return scope, scope_params

def get_scope_params(scope: Optional[str], file_path: Optional[str]) -> tuple[str,dict[str,Any]]:
    """Get scope parameters for profile operations."""
    # Set scope parameters
    scope_params = {
        "scope": scope,
        "file_path": file_path
    }

    # Normalize scope
    scope = ProfileParameterProcessor.resolve_scope(
        scope_params["scope"], scope_params["file_path"]
    )

    return scope, scope_params

def create_profile(ext_name: str, ext_profilemanager: ProfileManager, json_input: Optional[str], **kwargs):
    """Create a new profile for the extension."""

    (scope, scope_params) = extract_scope_params(**kwargs)

    # Initialize context 
    ctx = _initialize_context(scope_params)
    
    try:
        # Process parameters (from JSON or remaining keyword args)
        if json_input:
            profile_data = CreateProfileParameterProcessor.from_json(json_input)
        else:
            # kwargs now contains only the profile-specific parameters
            profile_data = CreateProfileParameterProcessor.from_args(kwargs)
        

        # Create profile
        created_profile = ext_profilemanager.create_profile(profile_data, scope)
        
        # Format output
        OutputFormatter.print_success(f"{ext_name} profile '{created_profile['name']}' created successfully.")
        OutputFormatter.print_json(created_profile, "Profile Details")
    except (ValueError, json.JSONDecodeError) as e:
        OutputFormatter.print_error(str(e))

def list_profiles(ext_name: str, ext_profilemanager: ProfileManager, 
                  profile_params:List[dict[str, Any]], scope: str, file_path: Optional[str], output_format: str):
    """List available profiles."""
    (scope, scope_params) = get_scope_params(scope, file_path)

    # Initialize context 
    ctx = _initialize_context(scope_params)

    try:
        # List profiles
        profiles = ext_profilemanager.list_profiles(scope)
        
        if not profiles:
            OutputFormatter.print_info(f"No {ext_name} profiles found in {scope} configuration.")
            return
        
        # Get default profile
        default_profile = ext_profilemanager.get_default_profile()
        
        # Format output
        if output_format == "json":
            OutputFormatter.print_json(profiles, "{ext_name} Profiles")
        else:  # table format
            # Prepare data for table
            table_data = []
            for name, profile in profiles.items():
                row = {}
                for param in profile_params:
                    row[param["name"].capitalize()] = profile.get(param["name"], None)
                table_data.append(row)

            table_header = [ param["name"].capitalize() for param in profile_params ]
            # Display table
            OutputFormatter.print_table(
                table_data,
                table_header,
                f"{ext_name} Profiles ({scope})"
            )
    except (ValueError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))

def show_profile(ext_name:str, ext_profilemanager: ProfileManager, 
                 name: str, scope: str, file_path: Optional[str], output_format: str):
    """Show profile details."""
    (scope, scope_params) = get_scope_params(scope, file_path)

    # Initialize context 
    ctx = _initialize_context(scope_params)
    
    try:
        # Get profile
        profile = ext_profilemanager.get_profile_from_scope(name, scope)
        
        # Format output
        if output_format == "json":
            OutputFormatter.print_json(profile, f"{ext_name} Profile: {name}")
        else:  # table format
            # Use our special profile formatter
            OutputFormatter.print_profile(profile, name)
    except (ValueError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))

def edit_profile(ext_name:str, ext_profilemanager: ProfileManager, 
                 name: str, json_input: Optional[str], **kwargs):
    """Edit an existing LLM profile."""
    (scope, scope_params) = extract_scope_params(**kwargs)

    # Initialize context 
    ctx = _initialize_context(scope_params)
    
    try:
        # Process parameters (from JSON or command-line args)
        if json_input:
            updates = EditProfileParameterProcessor.from_json(json_input, name)
        else:
            # Include the name parameter in the kwargs for processing
            kwargs["name"] = name
            # kwargs now contains all profile-specific parameters
            updates = EditProfileParameterProcessor.from_args(kwargs)
        
        # Edit profile
        updated_profile = ext_profilemanager.edit_profile(name, updates, scope)
        OutputFormatter.print_success(f"LLM profile '{name}' updated successfully.")
        OutputFormatter.print_json(updated_profile, "Updated Profile")
    except (ValueError, json.JSONDecodeError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))

def delete_profile(ext_name:str, ext_profilemanager: ProfileManager, 
                   name: str, scope: str, file_path: Optional[str]):
    """Delete a profile."""
    (scope, scope_params) = get_scope_params(scope, file_path)

    # Initialize context 
    ctx = _initialize_context(scope_params)
    
    try:
        
        # Delete profile
        ext_profilemanager.delete_profile(name, scope)
        OutputFormatter.print_success(f"{ext_name} profile '{name}' deleted successfully.")
    except (ValueError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))

def use_profile(ext_name: str, ext_profilemanager: ProfileManager, 
                name: str, scope: str, file_path: Optional[str]):
    """Use a specific ZZZ profile as default."""
    (scope, scope_params) = get_scope_params(scope, file_path)

    # Initialize context 
    ctx = _initialize_context(scope_params)

    
    try:
        
        # Set as default profile
        ext_profilemanager.use_profile(name, scope)
        OutputFormatter.print_success(f"{ext_name} profile '{name}' set as default in {scope} configuration.")
    except (ValueError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))