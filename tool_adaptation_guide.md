# Adapting the Universal CLI Base for Custom Tools

This guide explains how to modify the Universal CLI Base to create a specialized command-line tool with a custom name and functionality. We'll focus on:

1. Renaming the tool and its components
2. Adding new commands, options, parameters, and flags
3. Structuring new command modules

## 1. Renaming the Tool

### Step 1: Project Setup

First, fork or copy the existing CLI Base project and rename it:

```bash
# Clone the repository
git clone /path/to/cli_base my_custom_tool

# Enter the directory
cd my_custom_tool
```

### Step 2: Update Package Information

Modify the `pyproject.toml` file:

```toml
[project]
name = "my-custom-tool"  # Replace with your tool name
version = "0.1.0"
description = "Your custom tool description"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "python-dotenv>=1.0.1",
    "click>=8.1.7",
    "rich>=13.7.0",
    "pyyaml>=6.0.1",
    # Add any additional dependencies your tool needs
]

[project.scripts]
mytool = "my_custom_tool.main:cli"  # Replace "mytool" with your desired command name
```

### Step 3: Rename the Package Directory

Rename the `cli_base` directory to match your tool's name:

```bash
mv cli_base my_custom_tool
```

### Step 4: Update Import Statements

You'll need to update all import statements in the codebase to use the new package name. This can be done with a find-and-replace operation:

```bash
# For Unix/Linux/Mac
find . -name "*.py" -exec sed -i '' 's/from cli_base/from my_custom_tool/g' {} \;
find . -name "*.py" -exec sed -i '' 's/import cli_base/import my_custom_tool/g' {} \;

# For Windows (PowerShell)
Get-ChildItem -Path . -Filter *.py -Recurse | ForEach-Object {
    (Get-Content $_.FullName) | ForEach-Object {
        $_ -replace 'from cli_base', 'from my_custom_tool' `
           -replace 'import cli_base', 'import my_custom_tool'
    } | Set-Content $_.FullName
}
```

### Step 5: Update the README.md

Modify the README.md file to reflect your tool's name, description, and usage:

```markdown
# My Custom Tool

A specialized command-line tool based on the Universal CLI template.

## Installation

```
pip install -e .
```

## Usage

The tool follows this general structure:

```
mytool [COMMAND] [SUBCOMMAND] [OPTIONS] [FLAGS]
```

### Core Commands

- `command1`: Description of command1
- `command2`: Description of command2
- `config`: Manage configuration files
- `schema`: Display command structure as ASCII art
- `help`: Display help information
```

### Step 6: Update Default Configuration

Modify the default configuration in `my_custom_tool/utils/config.py` to include tool-specific settings:

```python
# Update the default configuration
DEFAULT_CONFIG = {
    "app": {
        "name": "my-custom-tool",
        "verbose": False,
        "quiet": False,
        # Add any other default settings your tool needs
    },
    # Keep existing configuration sections as needed
    "profiles": {},
    # Add new configuration sections specific to your tool
}
```

### Step 7: Update the Main Module

Modify the main module at `my_custom_tool/main.py` to include your tool's description and commands:

```python
#!/usr/bin/env python3
"""
My Custom Tool: A specialized command-line tool with standardized commands and configuration management.
"""

import click
from my_custom_tool.commands.config_cmd import config_group
from my_custom_tool.commands.schema_cmd import schema_group
# Import your custom command groups here

@click.group()
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
def cli(verbose: bool, quiet: bool):
    """
    My Custom Tool: A specialized command-line tool with standardized commands and configuration management.
    
    Use commands like 'command1', 'command2', 'config', and 'schema' to interact with the tool.
    """
    # Initialize runtime settings with global CLI arguments
    cli_args = {
        "verbose": verbose,
        "quiet": quiet
    }
    
    try:
        # Try to get existing context manager instance
        ctx = ContextManager.get_instance()
    except RuntimeError:
        # Initialize new context manager
        ctx = ContextManager.initialize(cli_args)

# Add command groups
cli.add_command(config_group)
cli.add_command(schema_group)
# Add your custom command groups here

# ... rest of the file remains the same
```

## 2. Adding New Commands

The CLI Base uses Click for command-line interface creation. Here's how to add new commands with various parameter types.

### Basic Command Structure

Commands are organized in a hierarchical structure:
- The main CLI object contains command groups
- Command groups contain commands
- Commands contain options, arguments, and flags

### Step 1: Create a New Command Module

Create a new file in the `my_custom_tool/commands/` directory:

```python
# my_custom_tool/commands/custom_cmd.py
"""
Custom command module.
Provides commands for custom functionality.
"""

import click
from ..utils.context import ContextManager
from ..utils.formatting import OutputFormatter

@click.group(name="custom")
def custom_group():
    """Custom commands for specific functionality."""
    pass

# Add this command group to main.py:
# from my_custom_tool.commands.custom_cmd import custom_group
# cli.add_command(custom_group)
```

### Step 2: Add Commands with Different Parameter Types

Here are examples of different command patterns:

#### Simple Command with No Parameters

```python
@custom_group.command(name="version")
def show_version():
    """Display the current version."""
    OutputFormatter.print_info("My Custom Tool v1.0.0")
```

#### Command with Required Arguments

```python
@custom_group.command(name="process")
@click.argument("input_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
def process_file(input_file):
    """
    Process the specified input file.
    
    INPUT_FILE: Path to the file to process
    """
    OutputFormatter.print_info(f"Processing file: {input_file}")
    # Implementation...
```

#### Command with Optional Arguments

```python
@custom_group.command(name="search")
@click.argument("query", required=False)
def search(query):
    """
    Search for items matching the query.
    
    QUERY: Optional search term
    """
    if query:
        OutputFormatter.print_info(f"Searching for: {query}")
    else:
        OutputFormatter.print_info("No search query provided")
    # Implementation...
```

#### Command with Multiple Arguments

```python
@custom_group.command(name="copy")
@click.argument("source", type=click.Path(exists=True))
@click.argument("destination", type=click.Path())
def copy_file(source, destination):
    """
    Copy a file from source to destination.
    
    SOURCE: Source file path
    DESTINATION: Destination file path
    """
    OutputFormatter.print_info(f"Copying {source} to {destination}")
    # Implementation...
```

#### Command with Variable Number of Arguments

```python
@custom_group.command(name="analyze")
@click.argument("files", nargs=-1, type=click.Path(exists=True))
def analyze_files(files):
    """
    Analyze multiple files.
    
    FILES: One or more file paths to analyze
    """
    OutputFormatter.print_info(f"Analyzing {len(files)} files")
    for file in files:
        OutputFormatter.print_info(f"  - {file}")
    # Implementation...
```

#### Command with Options (Flags and Values)

```python
@custom_group.command(name="generate")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", type=click.Choice(["json", "yaml", "csv"]), default="json", help="Output format")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--count", "-n", type=int, default=10, help="Number of items to generate")
def generate(output, format, verbose, count):
    """Generate sample data."""
    if verbose:
        OutputFormatter.print_info(f"Generating {count} items in {format} format")
        if output:
            OutputFormatter.print_info(f"Output will be saved to {output}")
    # Implementation...
```

#### Command with Required Options

```python
@custom_group.command(name="configure")
@click.option("--api-key", required=True, help="API key for authentication")
@click.option("--endpoint", required=True, help="API endpoint URL")
def configure(api_key, endpoint):
    """Configure API settings."""
    OutputFormatter.print_info(f"Configuring API endpoint: {endpoint}")
    # Implementation...
```

#### Command with Password Prompt

```python
@custom_group.command(name="login")
@click.option("--username", "-u", prompt=True, help="Username for authentication")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Password for authentication")
def login(username, password):
    """Log in to the service."""
    OutputFormatter.print_info(f"Logging in as {username}")
    # Implementation...
```

#### Command with Confirmation

```python
@custom_group.command(name="delete")
@click.argument("item_id")
@click.confirmation_option(prompt="Are you sure you want to delete this item?")
def delete_item(item_id):
    """Delete an item (with confirmation)."""
    OutputFormatter.print_success(f"Item {item_id} deleted successfully")
    # Implementation...
```

#### Command with Custom Callbacks

```python
def validate_range(ctx, param, value):
    if value is not None and (value < 1 or value > 100):
        raise click.BadParameter("Value must be between 1 and 100")
    return value

@custom_group.command(name="set-limit")
@click.option("--limit", type=int, callback=validate_range, help="Set the limit (1-100)")
def set_limit(limit):
    """Set processing limit with custom validation."""
    if limit is not None:
        OutputFormatter.print_info(f"Limit set to {limit}")
    # Implementation...
```

### Step 3: Create Subcommands

You can create nested command hierarchies:

```python
@custom_group.group(name="config")
def custom_config_group():
    """Manage custom configuration."""
    pass

@custom_config_group.command(name="set")
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    """Set a configuration value."""
    OutputFormatter.print_info(f"Setting {key}={value}")
    # Implementation...

@custom_config_group.command(name="get")
@click.argument("key")
def get_config(key):
    """Get a configuration value."""
    OutputFormatter.print_info(f"Getting value for {key}")
    # Implementation...
```

### Step 4: Creating Command Decorators for Reuse

For commonly used option combinations, create decorator functions:

```python
# my_custom_tool/commands/cmd_options.py
import click

def common_output_options(command):
    """Decorator to add common output options to a command."""
    command = click.option(
        "--output", "-o", 
        type=click.Path(), 
        help="Output file path"
    )(command)
    
    command = click.option(
        "--format", "-f", 
        type=click.Choice(["json", "yaml", "csv"]), 
        default="json", 
        help="Output format"
    )(command)
    
    return command

# Usage in your command module:
@custom_group.command(name="export")
@common_output_options
def export_data(output, format):
    """Export data with common output options."""
    OutputFormatter.print_info(f"Exporting data in {format} format")
    if output:
        OutputFormatter.print_info(f"Output will be saved to {output}")
    # Implementation...
```

## 3. Updating the Schema System

The schema system needs to be updated to work with your renamed tool. There are two possible approaches depending on your codebase's current implementation:

### 3.1 Static Schema Definition

If your schema is defined with a static `SCHEMA_DATA` dictionary in `schema_cmd.py`:

1. Update the file at `my_custom_tool/commands/schema_cmd.py`:

```python
# Update the SCHEMA_DATA dictionary with your new commands
SCHEMA_DATA = {
    "config": {
        "help": "Manage configuration files",
        "subcommands": {
            # configuration subcommands...
        }
    },
    "custom": {
        "help": "Custom commands for specific functionality",
        "subcommands": {
            "version": {"help": "Display the current version", "options": {}},
            "process": {
                "help": "Process the specified input file",
                "options": {
                    "INPUT_FILE": "Path to the file to process"
                }
            },
            # ... other commands ...
        }
    },
    "schema": {
        "help": "Display command structure as ASCII art",
        "subcommands": {}
    },
    "help": {
        "help": "Display help information",
        "subcommands": {}
    }
}
```

2. Update any references to the original tool name in the schema module:

```python
@click.group(name="schema")
def schema_group():
    """Display command structure of my-custom-tool as ASCII art."""
    pass

@schema_group.command(name="show")
@click.argument("command", required=False)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def show_schema(command: str, verbose: bool):
    """Show schema for a specific command or the entire CLI."""
    # ... implementation ...
    
    # If using OutputFormatter, ensure any references to the CLI name are updated:
    if not command:
        # Show schema for all commands
        OutputFormatter.print_command_tree(SCHEMA_DATA, title="My Custom Tool Commands")
```

### 3.2 Dynamic Schema with Command Registry

If your project uses the `CommandRegistry` system (recommended for tools with dynamically created commands):

1. Modify the `CommandRegistry` class in `my_custom_tool/utils/command_registry.py`:

```python
class CommandRegistry:
    # ... existing implementation ...
    
    @staticmethod
    def print_command_tree(schema_data):
        """Print a visual representation of the command structure."""
        console = Console()
        # Update the tool name in the tree title
        tree = Tree("📋 [bold yellow]My Custom Tool[/bold yellow]")
        
        # ... rest of the method ...
```

2. Update the schema command to use the registry:

```python
# my_custom_tool/commands/schema_cmd.py
import click
from ..utils.context import ContextManager
from ..utils.formatting import OutputFormatter
from ..utils.command_registry import CommandRegistry

@click.group(name="schema")
def schema_group():
    """Display command structure of My Custom Tool as ASCII art."""
    pass

@schema_group.command(name="show")
@click.argument("command", required=False)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def show_schema(command: str, verbose: bool):
    """Show schema for a specific command or the entire CLI."""
    # Ensure context is initialized
    try:
        ctx = ContextManager.get_instance()
    except RuntimeError:
        ctx = ContextManager.initialize({"verbose": verbose})
    
    # Get command registry
    registry = CommandRegistry.get_instance()
    
    if command:
        # Show schema for specific command
        if registry.get_command(command):
            command_schema = registry.get_schema(command)
            OutputFormatter.print_command_tree(command_schema, title=f"Command: {command}")
        else:
            # Command not found
            OutputFormatter.print_error(f"Command not found: {command}")
    else:
        # Show schema for all commands
        schema_data = registry.get_schema()
        OutputFormatter.print_command_tree(schema_data, title="My Custom Tool Commands")
```

3. Ensure command registration is properly initialized in `main.py`:

```python
# At the end of main.py, after all commands are added
from my_custom_tool.utils.command_registry import CommandRegistry
registry = CommandRegistry.get_instance()
registry.register_commands_from_cli(cli)
```

### 3.3 Update Formatting Utilities

Look for any hardcoded references to the original tool name in formatting utilities:

1. Check `my_custom_tool/utils/formatting.py`:

```python
class OutputFormatter:
    # ...
    
    @staticmethod
    def print_command_tree(schema_data, title="Command Structure"):
        """Print a visual representation of the command structure."""
        console = Console()
        # Update the title to use your custom tool name if needed
        tree = Tree(f"📋 [bold yellow]{title}[/bold yellow]")
        
        # ... rest of the method ...
```

2. Update any ASCII art or formatted outputs that might reference the tool name.

## 4. Installing and Testing

Install your renamed package:

```bash
pip install -e .
```

Test the tool with your new name:

```bash
# Check the basic help
mytool --help

# Try the schema command
mytool schema show

# Try your new commands
mytool custom version
mytool custom generate --format yaml --count 5
```

## Summary of Command Parameter Types

| Type | Description | Example |
|------|-------------|---------|
| Argument | Positional parameter | `@click.argument("name")` |
| Option | Named parameter with value | `@click.option("--name", "-n")` |
| Flag | Boolean option | `@click.option("--verbose", is_flag=True)` |
| Choice | Option with predefined choices | `@click.option("--format", type=click.Choice(["json", "csv"]))` |
| Path | File or directory path | `@click.option("--file", type=click.Path(exists=True))` |
| Multiple | Option that can be specified multiple times | `@click.option("--tag", multiple=True)` |
| Prompt | Interactive prompt for value | `@click.option("--name", prompt=True)` |
| Password | Hidden input prompt | `@click.option("--password", hide_input=True)` |
| Confirmation | Requires confirmation | `@click.confirmation_option()` |
| Custom validation | Validate with callback | `@click.option("--n", callback=validate_func)` |

## Command Groups vs. Individual Commands

- **Command Groups (`@click.group()`)**: Create a collection of related commands
- **Commands (`@command_group.command()`)**: Individual actions within a group
- **Nested Groups (`@command_group.group()`)**: Create hierarchical command structures

When designing your command structure:
1. Group related commands together
2. Use consistent naming conventions
3. Keep the hierarchy shallow (no more than 2-3 levels deep)
4. Make command and option names self-explanatory

By following these guidelines, you can transform the Universal CLI Base into a custom tool with your own branding and specialized commands.