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

#### B. Update Command Functions

```python
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
def create_profile(**kwargs):
    """Create a new LLM profile."""
    # Initialize context and LLM manager
    ctx = _initialize_context({"scope": kwargs.get("scope"), "file_path": kwargs.get("file_path")})
    llm_manager = LLMProfileManager()
    
    try:
        # Process parameters (from JSON or command-line args)
        if kwargs.get("json_input"):
            profile_data = CreateProfileParameterProcessor.from_json(kwargs.get("json_input"))
        else:
            profile_data = CreateProfileParameterProcessor.from_args(kwargs)
        
        # Normalize scope
        scope = ProfileParameterProcessor.validate_scope(kwargs.get("scope"), kwargs.get("file_path"))
        
        # Create profile
        created_profile = llm_manager.create_profile(profile_data, scope)
        
        # Format output
        OutputFormatter.print_success(f"LLM profile '{created_profile['name']}' created successfully.")
        OutputFormatter.print_json(created_profile, "Profile Details")
    except (ValueError, json.JSONDecodeError) as e:
        OutputFormatter.print_error(str(e))
```

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