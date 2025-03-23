# Supporting Simple Commands in cli_base

This document explains the changes required in the cli_base framework to support simple Click commands alongside command groups.

## Problem Statement

The cli_base framework was initially designed to work with command groups (commands with subcommands), but not with simple commands. When trying to add the `capture` command, which is a simple command without subcommands, we encountered errors because the command registry and formatting utilities expected all commands to be groups.

## Key Components That Needed Changes

Two main components needed updates to support simple commands:

1. **CommandRegistry**: Responsible for registering commands and extracting their schema information
2. **OutputFormatter**: Responsible for displaying command information, including the schema visualization

## Changes to CommandRegistry

### 1. Update Type Hints and Method Signatures

All methods that previously only accepted `click.Group` needed to be updated to accept either `click.Group` or `click.Command`:

```python
# Before
def register_command(self, command_name: str, command_group: click.Group, schema: Dict[str, Any]) -> None:
    # ...

# After
def register_command(self, command_name: str, command: Union[click.Group, click.Command], schema: Dict[str, Any]) -> None:
    # ...
```

Similarly for other methods like `get_command` and `get_all_commands`.

### 2. Enhance the Schema Extraction Logic

The `extract_schema_from_command` method needed significant changes to handle both command types:

```python
def extract_schema_from_command(self, command_name: str, command: Union[click.Group, click.Command]) -> Dict[str, Any]:
    """
    Extract schema information from a command or command group.
    """
    # Get help text from command docstring
    help_text = command.help or f"Manage {command_name}"
    
    # Initialize schema
    schema = {
        "help": help_text,
        "subcommands": {}
    }
    
    # Check if this is a command group or a simple command
    if isinstance(command, click.Group) and hasattr(command, 'commands'):
        # Process command group - extract subcommands and their options
        for subcmd_name, subcmd in command.commands.items():
            # [Process subcommands as before]
            # ...
    else:
        # For simple commands, add options directly to the main schema
        options_schema = {}
        for param in command.params:
            if isinstance(param, click.Option):
                # [Extract option details]
                # ...
        
        # Add options to the main schema
        schema["options"] = options_schema
    
    return schema
```

### 3. Update Command Registration Logic

The `register_commands_from_cli` method needed to be updated to register all commands, not just command groups:

```python
def register_commands_from_cli(self, cli: click.Group) -> None:
    """Register all commands from a CLI group."""
    for cmd_name, cmd in cli.commands.items():
        # Extract schema for both groups and simple commands (no type check)
        schema = self.extract_schema_from_command(cmd_name, cmd)
        # Register command or command group
        self.register_command(cmd_name, cmd, schema)
```

## Changes to OutputFormatter

The `print_command_tree` method in the OutputFormatter class needed to be enhanced to display options for simple commands:

```python
@staticmethod
def print_command_tree(commands: Dict[str, Any]) -> None:
    """Print a formatted command tree structure with vibrant colors."""
    tree = Tree(f"[command]cli_base[/command]", guide_style="blue")
    
    # Commands section
    cmd_section = tree.add(f"[section]COMMANDS[/section]")
    for cmd_name, cmd_info in commands.items():
        cmd_node = cmd_section.add(
            f"[command]{cmd_name}[/command]                [value]{cmd_info.get('help', '')}[/value]"
        )
        
        # Add subcommands if any
        if "subcommands" in cmd_info and cmd_info["subcommands"]:
            # [Process subcommands as before]
            # ...
        
        # Add options for simple commands
        if "options" in cmd_info:
            for opt_name, opt_help in cmd_info["options"].items():
                cmd_node.add(f"[option]{opt_name}[/option] [value]{opt_help}[/value]")
    
    # [Rest of the method as before]
    # ...
```

## Impact of These Changes

These changes allow the cli_base framework to:

1. **Register Any Command Type**: Both command groups (like `llm`) and simple commands (like `capture`) can be registered and used
2. **Consistent Schema Handling**: Schema information is extracted correctly from both types of commands
3. **Proper Visualization**: The command tree visualization shows options for simple commands, making them discoverable
4. **Type Safety**: Updated type hints ensure code maintainability

## Best Practices for Adding New Commands

When adding a new command to cli_base, you now have two options:

### 1. Command Group (Multiple Related Commands)

```python
@click.group(name="mygroup")
def mygroup_cmd():
    """My command group description."""
    pass

@mygroup_cmd.command(name="subcommand")
def subcommand():
    """Subcommand description."""
    # Implementation
```

### 2. Simple Command (Single Functionality)

```python
@click.command(name="mysimplecmd")
@click.option("--option1", help="Option description")
def simple_cmd(option1):
    """Simple command description."""
    # Implementation
```

In either case, the command can be added to the CLI in `main.py`:

```python
# Add to CLI
cli.add_command(mygroup_cmd)  # For command group
cli.add_command(simple_cmd)   # For simple command
```

No explicit registration with CommandRegistry is needed for either type, as it's now handled automatically by the CLI registration process.

## Conclusion

These enhancements make the cli_base framework more flexible and capable of handling a wider variety of command patterns. The changes maintain backward compatibility with existing command groups while enabling new simple commands to be added easily.