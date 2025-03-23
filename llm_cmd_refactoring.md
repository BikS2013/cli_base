# LLM Command Module Refactoring

## Current Structure

Currently, the `llm_cmd.py` file handles all commands related to LLM profiles using a single approach for both command-line arguments and JSON input. This creates some inefficiencies and makes the code less maintainable:

1. The same code handles both individual CLI arguments (--name, --provider, etc.) and a JSON structure
2. Validation logic is mixed with command parsing
3. Command handlers are lengthy and have duplicated code

## Proposed Changes

I propose refactoring the LLM command module to better separate concerns and improve maintainability:

### 1. Create Command-Specific Parameter Handlers

Create separate handler functions for each command that will:
- Process command-line arguments
- Process JSON input
- Validate inputs for the specific command
- Return a clean, validated data structure

### 2. Restructure Command Functions

Each command function will:
1. Parse input parameters using the specific handler
2. Execute the business logic
3. Format and output the results

### 3. Core Implementation Changes

#### A. Create Parameter Processing Classes

```python
class ProfileParameterProcessor:
    """Base class for processing profile parameters."""
    
    @staticmethod
    def validate_scope(scope: str, file_path: Optional[str]) -> str:
        """Validate and normalize scope parameter."""
        if scope is None and file_path is not None:
            return "file"
        return scope or "local"  # Default to local
    
    @staticmethod
    def process_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate generic parameters."""
        # Basic validation
        if not params.get("name"):
            raise ValueError("Profile name is required")
        return params


class CreateProfileParameterProcessor(ProfileParameterProcessor):
    """Process parameters for profile creation."""
    
    @classmethod
    def from_args(cls, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process parameters from command-line arguments."""
        # Extract required fields
        profile_data = {
            "name": args.get("name"),
            "provider": args.get("provider"),
            "model": args.get("model"),
            "api_key": args.get("api_key")
        }
        
        # Add optional fields if provided
        for field in ["deployment", "base_url", "api_version"]:
            if args.get(field):
                profile_data[field] = args.get(field)
        
        if args.get("temperature") is not None:
            profile_data["temperature"] = args.get("temperature")
            
        return cls.process_params(profile_data)
    
    @classmethod
    def from_json(cls, json_str: str) -> Dict[str, Any]:
        """Process parameters from JSON input."""
        try:
            profile_data = json.loads(json_str)
            return cls.process_params(profile_data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
```

#### B. Using Generic Approach with Variable Keyword Arguments

Using a more generic approach with `**profileargs` is indeed feasible with Click. This approach will make the code more maintainable and adaptable to future changes in profile parameters.

There are two main ways to implement this:

1. Use Click's advanced callback pattern to process all options generically
2. Use `**kwargs` to receive all options and filter them in the function

Here's how we can implement this:

```python
# Define profile parameters dynamically
PROFILE_PARAMS = [
    {"name": "name", "type": str, "help": "Profile name"},
    {"name": "provider", "type": str, "help": "LLM provider (e.g., openai, anthropic)"},
    {"name": "model", "type": str, "help": "Model name"},
    {"name": "deployment", "type": str, "help": "Deployment name (for Azure)"},
    {"name": "api_key", "type": str, "help": "API key"},
    {"name": "base_url", "type": str, "help": "Base URL for API"},
    {"name": "api_version", "type": str, "help": "API version"},
    {"name": "temperature", "type": float, "help": "Temperature (0.0-1.0)"}
]

# Helper function to add options dynamically
def add_profile_options(command):
    """Decorator to add profile options to a command."""
    for param in PROFILE_PARAMS:
        command = click.option(
            f"--{param['name']}", 
            type=param['type'], 
            help=param['help']
        )(command)
    return command

# Apply options using the decorator
@llm_group.command(name="create")
@add_profile_options
@click.option("--global", "scope", flag_value="global", help="Use global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Use local configuration.")
@click.option("--file", "file_path", type=str, help="Use named configuration file.")
@click.argument("json_input", required=False)
def create_profile(json_input: Optional[str], **kwargs):
    """Create a new LLM profile."""
    # Extract scope parameters
    scope_params = {
        "scope": kwargs.pop("scope", None),
        "file_path": kwargs.pop("file_path", None)
    }
    
    # Initialize context and LLM manager
    ctx = _initialize_context(scope_params)
    llm_manager = LLMProfileManager()
    
    try:
        # Process parameters (from JSON or remaining keyword args)
        if json_input:
            profile_data = CreateProfileParameterProcessor.from_json(json_input)
        else:
            # kwargs now contains only the profile-specific parameters
            profile_data = CreateProfileParameterProcessor.from_args(kwargs)
        
        # Normalize scope
        scope = ProfileParameterProcessor.validate_scope(
            scope_params["scope"], scope_params["file_path"]
        )
        
        # Create profile
        created_profile = llm_manager.create_profile(profile_data, scope)
        
        # Format output
        OutputFormatter.print_success(f"LLM profile '{created_profile['name']}' created successfully.")
        OutputFormatter.print_json(created_profile, "Profile Details")
    except (ValueError, json.JSONDecodeError) as e:
        OutputFormatter.print_error(str(e))
```

#### Alternative Approach with Explicit Parameter Collection

An alternative approach that's more explicit about the profile parameters:

```python
@llm_group.command(name="create")
@click.argument("json_input", required=False)
@click.option("--name", type=str, help="Profile name")
# Add more options for other profile parameters
@click.option("--global", "scope", flag_value="global", help="Use global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Use local configuration.")
@click.option("--file", "file_path", type=str, help="Use named configuration file.")
def create_profile(
    json_input: Optional[str],
    name: Optional[str] = None,
    scope: Optional[str] = None,
    file_path: Optional[str] = None,
    **profileargs  # Catches all other profile-related options
):
    """Create a new LLM profile."""
    # Initialize context and LLM manager
    ctx = _initialize_context({"scope": scope, "file_path": file_path})
    llm_manager = LLMProfileManager()
    
    try:
        if json_input:
            profile_data = CreateProfileParameterProcessor.from_json(json_input)
        else:
            # Combine explicitly named parameters with the rest in profileargs
            all_profile_args = {"name": name, **profileargs}
            # Remove None values
            profile_data = {k: v for k, v in all_profile_args.items() if v is not None}
            profile_data = CreateProfileParameterProcessor.validate(profile_data)
        
        # Normalize scope
        scope = ProfileParameterProcessor.validate_scope(scope, file_path)
        
        # Create profile
        created_profile = llm_manager.create_profile(profile_data, scope)
        
        # Format output
        OutputFormatter.print_success(f"LLM profile '{created_profile['name']}' created successfully.")
        OutputFormatter.print_json(created_profile, "Profile Details")
    except (ValueError, json.JSONDecodeError) as e:
        OutputFormatter.print_error(str(e))
```

### Considerations for Using Variable Keyword Arguments

1. **Type Hints**: With the `**profileargs` approach, you lose explicit type hints for each parameter, which might affect IDE autocompletion and static type checking.

2. **Documentation**: Command help will still show each parameter individually, but the function signature won't match the help, which might be confusing during development.

3. **Validation**: You need to be more careful with validation since you're accepting arbitrary keyword arguments.

4. **Maintainability**: This approach is more maintainable when parameter lists grow large or change frequently, as you don't need to update function signatures.

5. **Click Compatibility**: Click does support this pattern, but it's less common in Click applications, so it might be less familiar to developers used to Click.

### Additional Implementation: Dynamic Parameters with TypedDict

For better type safety while using variable keyword arguments, we can use Python's `TypedDict` to define the expected parameter structure:

```python
from typing import TypedDict, Optional

class LLMProfileParams(TypedDict, total=False):
    name: str
    provider: str
    model: str
    deployment: Optional[str]
    api_key: str
    base_url: Optional[str]
    api_version: Optional[str]
    temperature: Optional[float]

@llm_group.command(name="create")
@click.argument("json_input", required=False)
@click.option("--name", type=str, help="Profile name")
# ... other profile options
@click.option("--global", "scope", flag_value="global", help="Use global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Use local configuration.")
@click.option("--file", "file_path", type=str, help="Use named configuration file.")
def create_profile(
    json_input: Optional[str],
    name: Optional[str] = None,
    scope: Optional[str] = None,
    file_path: Optional[str] = None,
    **profileargs
):
    """Create a new LLM profile."""
    # Type hints will now recognize profileargs as having LLMProfileParams structure
    profile_args: LLMProfileParams = {"name": name, **profileargs}
    
    # Rest of implementation...
```

This approach provides better type checking while still allowing for the flexible structure you requested.

## Extending the Generic Approach to Edit Profile Command

The `edit_profile` command can also benefit from the same generic approach. Like the `create_profile` command, it handles many profile parameters and would be more maintainable with a more generic structure.

### Current Edit Profile Command

```python
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
    # ... implementation ...
```

### Refactored Edit Profile Command with Generic Parameters

```python
@llm_group.command(name="edit")
@click.option("--name", type=str, required=True, help="Profile name")
@add_profile_options  # Reuse the same decorator we created for create_profile
@click.option("--global", "scope", flag_value="global", help="Edit in global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Edit in local configuration.")
@click.option("--file", "file_path", type=str, help="Edit in named configuration file.")
@click.argument("json_input", required=False)
def edit_profile(name: str, json_input: Optional[str], **kwargs):
    """Edit an existing LLM profile."""
    # Extract scope parameters
    scope_params = {
        "scope": kwargs.pop("scope", None),
        "file_path": kwargs.pop("file_path", None)
    }
    
    # Initialize context and LLM manager
    ctx = _initialize_context(scope_params)
    llm_manager = LLMProfileManager()
    
    try:
        # Process parameters (from JSON or command-line args)
        if json_input:
            updates = EditProfileParameterProcessor.from_json(json_input, name)
        else:
            # Include the name parameter in the kwargs for processing
            kwargs["name"] = name
            # kwargs now contains all profile-specific parameters
            updates = EditProfileParameterProcessor.from_args(kwargs)
        
        # Normalize scope
        scope = ProfileParameterProcessor.validate_scope(
            scope_params["scope"], scope_params["file_path"]
        )
        
        # Edit profile
        updated_profile = llm_manager.edit_profile(name, updates, scope)
        OutputFormatter.print_success(f"LLM profile '{name}' updated successfully.")
        OutputFormatter.print_json(updated_profile, "Updated Profile")
    except (ValueError, json.JSONDecodeError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))
```

### Adding the Edit Profile Parameter Processor

```python
class EditProfileParameterProcessor(ProfileParameterProcessor):
    """Process parameters for profile editing."""
    
    @classmethod
    def from_args(cls, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process parameters from command-line arguments."""
        # Filter out None values to only update provided fields
        updates = {k: v for k, v in args.items() if v is not None}
        
        # Ensure name is included
        if "name" not in updates:
            raise ValueError("Profile name is required for editing")
            
        return cls.process_params(updates)
    
    @classmethod
    def from_json(cls, json_str: str, profile_name: str) -> Dict[str, Any]:
        """Process parameters from JSON input with a required profile name."""
        try:
            updates = json.loads(json_str)
            
            # Ensure name is preserved if already in the JSON
            if "name" not in updates:
                updates["name"] = profile_name
                
            return cls.process_params(updates)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
```

### Alternative with TypedDict for Edit Profile

```python
@llm_group.command(name="edit")
@click.option("--name", type=str, required=True, help="Profile name")
# ... other profile options
@click.option("--global", "scope", flag_value="global", help="Edit in global configuration.")
@click.option("--local", "scope", flag_value="local", default=True, help="Edit in local configuration.")
@click.option("--file", "file_path", type=str, help="Edit in named configuration file.")
@click.argument("json_input", required=False)
def edit_profile(
    name: str,
    json_input: Optional[str] = None,
    scope: Optional[str] = None,
    file_path: Optional[str] = None,
    **profileargs
):
    """Edit an existing LLM profile."""
    # Initialize context and LLM manager
    ctx = _initialize_context({"scope": scope, "file_path": file_path})
    llm_manager = LLMProfileManager()
    
    try:
        if json_input:
            updates = json.loads(json_input)
            # Ensure name is preserved
            if "name" not in updates:
                updates["name"] = name
        else:
            # Type hint with our TypedDict
            profile_updates: LLMProfileParams = {"name": name}
            
            # Add all non-None values from profileargs
            for key, value in profileargs.items():
                if value is not None:
                    profile_updates[key] = value
        
        # Normalize scope
        scope = ProfileParameterProcessor.validate_scope(scope, file_path)
        
        # Edit profile
        updated_profile = llm_manager.edit_profile(name, profile_updates, scope)
        OutputFormatter.print_success(f"LLM profile '{name}' updated successfully.")
        OutputFormatter.print_json(updated_profile, "Updated Profile")
    except (ValueError, json.JSONDecodeError, FileNotFoundError) as e:
        OutputFormatter.print_error(str(e))
```

## Unifying Profile Command Parameters

To further improve code organization and reduce duplication, we can create a common parametrization function for all profile-related commands:

```python
def parametrize_profile_command(command_func, require_name=False):
    """
    Apply all profile-related parameters to a Click command function.
    
    Args:
        command_func: The Click command function to parametrize
        require_name: Whether the name parameter is required
    
    Returns:
        The parametrized Click command function
    """
    # Add name parameter with appropriate required setting
    command_func = click.option(
        "--name", 
        type=str, 
        required=require_name,
        help="Profile name"
    )(command_func)
    
    # Add other profile parameters
    for param in PROFILE_PARAMS:
        if param["name"] != "name":  # Skip name as we've already added it
            command_func = click.option(
                f"--{param['name']}", 
                type=param['type'], 
                help=param['help']
            )(command_func)
    
    # Add scope parameters
    command_func = click.option(
        "--global", "scope", flag_value="global", 
        help="Use global configuration."
    )(command_func)
    
    command_func = click.option(
        "--local", "scope", flag_value="local", default=True,
        help="Use local configuration."
    )(command_func)
    
    command_func = click.option(
        "--file", "file_path", type=str,
        help="Use named configuration file."
    )(command_func)
    
    # Add JSON input argument
    command_func = click.argument("json_input", required=False)(command_func)
    
    return command_func
```

Then we can simplify both command definitions:

```python
@llm_group.command(name="create")
@parametrize_profile_command
def create_profile(json_input: Optional[str] = None, **kwargs):
    """Create a new LLM profile."""
    # Implementation using kwargs...

@llm_group.command(name="edit")
@parametrize_profile_command(require_name=True)
def edit_profile(json_input: Optional[str] = None, **kwargs):
    """Edit an existing LLM profile."""
    # Implementation using kwargs...
```

This unified approach ensures consistent parameter handling across commands and makes adding new profile commands much easier in the future.

### 4. Helper Functions

```python
def _initialize_context(cli_args: Dict[str, Any]) -> ContextManager:
    """Initialize or get the context manager instance."""
    try:
        return ContextManager.get_instance()
    except RuntimeError:
        return ContextManager.initialize(cli_args)
```

## Benefits of the Refactoring

1. **Separation of Concerns**: The parameter processing is separated from the command logic
2. **Improved Maintainability**: Each command has a focused purpose with clear, reusable components
3. **Better Validation**: Parameter validation is consistently applied regardless of input source
4. **Enhanced Extensibility**: Adding new parameters or commands becomes easier
5. **Cleaner Code**: Reduced duplication and more readable command functions

## Implementation Plan

1. Create the parameter processing classes
2. Refactor each command function individually, starting with `create_profile`
3. Add helper functions to reduce duplication
4. Update tests to ensure functionality is preserved
5. Document the new approach

This refactoring maintains the same public API for users, so the CLI interface remains unchanged while improving the internal code structure.