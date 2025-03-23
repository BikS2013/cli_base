"""
Formatting utilities for CLI tool output.
Provides colorful and structured terminal output.
"""

from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.syntax import Syntax
from rich.theme import Theme
from rich import box
from typing import Dict, List, Any, Optional, Union

# Define a custom theme for the CLI
cli_theme = Theme({
    "command": "bright_cyan",
    "subcommand": "blue",
    "option": "green",
    "value": "white",
    "success": "green",
    "warning": "yellow",
    "error": "red bold",
    "info": "blue",
    "title": "magenta bold",
    "header": "yellow bold",
    "highlight": "cyan",
    "section": "yellow bold",
    "key": "cyan",
    "default": "green italic",
})

console = Console(theme=cli_theme)

class OutputFormatter:
    """Formats CLI output with color and structure."""
    
    @staticmethod
    def print_success(message: str) -> None:
        """Print a success message in green."""
        console.print(f"[success]{message}[/success]")
    
    @staticmethod
    def print_warning(message: str) -> None:
        """Print a warning message in yellow."""
        console.print(f"[warning]{message}[/warning]")
    
    @staticmethod
    def print_error(message: str) -> None:
        """Print an error message in red."""
        console.print(f"[error]{message}[/error]")
    
    @staticmethod
    def print_info(message: str) -> None:
        """Print an informational message in blue."""
        console.print(f"[info]{message}[/info]")
    
    @staticmethod
    def print_json(data: Dict[str, Any], title: Optional[str] = None) -> None:
        """Print data as formatted JSON with color highlighting."""
        import json
        
        # Convert data to a formatted JSON string
        json_str = json.dumps(data, indent=2)
        
        # Create a syntax highlighted JSON
        syntax = Syntax(
            json_str, 
            "json", 
            theme="monokai",
            word_wrap=True,
            line_numbers=False,
            indent_guides=True,
        )
        
        if title:
            panel = Panel(
                syntax,
                title=f"[title]{title}[/title]",
                border_style="blue",
                expand=False,
                padding=(1, 2)
            )
            console.print(panel)
        else:
            console.print(syntax)
    
    @staticmethod
    def print_table(
        data: List[Dict[str, Any]], 
        columns: List[str], 
        title: Optional[str] = None,
        box_style: box.Box = box.ROUNDED
    ) -> None:
        """Print data as a colored table."""
        # Create a table with a border style
        table = Table(
            title=f"[title]{title}[/title]" if title else None,
            box=box_style, 
            show_header=True, 
            header_style="header",
            title_style="title",
            border_style="blue"
        )
        
        # Add columns with color styles
        for column in columns:
            # Special styling for specific columns
            if column.lower() in ["name", "key", "property"]:
                style = "key"
            elif column.lower() == "default":
                style = "default"
            elif column.lower() in ["provider", "model"]:
                style = "highlight"
            else:
                style = "white"
            
            table.add_column(column, style=style)
        # Add rows with appropriate styling
        for row in data:
            row_values = []
            for col in columns:
                value = str(row.get(col, ""))
                #print( f"from row: {row} and col: {col} the value is: {value}")
                # Special styling for the "Default" column with a checkmark
                if col == "Default" and value == "✓":
                    value = f"[default]{value}[/default]"
                
                row_values.append(value)
            
            table.add_row(*row_values)
        
        console.print(table)
    
    @staticmethod
    def print_tree(
        tree_data: Dict[str, Any], 
        title: str = "Command Structure",
        show_values: bool = True
    ) -> None:
        """Print a hierarchical tree structure with color coding."""
        tree = Tree(f"[command]{title}[/command]", guide_style="blue")
        
        def add_nodes(parent, data):
            for key, value in data.items():
                if isinstance(value, dict):
                    node = parent.add(f"[key]{key}[/key]")
                    add_nodes(node, value)
                elif isinstance(value, list):
                    node = parent.add(f"[section]{key}[/section]")
                    for item in value:
                        if isinstance(item, dict):
                            subnode = node.add(f"[option]{item.get('name', 'Item')}[/option]")
                            for k, v in item.items():
                                if k != 'name' and show_values:
                                    subnode.add(f"[key]{k}:[/key] [value]{v}[/value]")
                        else:
                            node.add(f"[value]{item}[/value]")
                elif show_values:
                    parent.add(f"[key]{key}:[/key] [value]{value}[/value]")
        
        add_nodes(tree, tree_data)
        console.print(tree)
    
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
                for subcmd_name, subcmd_info in cmd_info["subcommands"].items():
                    subcmd_node = cmd_node.add(
                        f"[subcommand]{subcmd_name}[/subcommand]            [value]{subcmd_info.get('help', '')}[/value]"
                    )
                    
                    # Add options if any
                    if "options" in subcmd_info:
                        for opt_name, opt_help in subcmd_info["options"].items():
                            subcmd_node.add(f"[option]{opt_name}[/option] [value]{opt_help}[/value]")
            
            # Add options for simple commands
            if "options" in cmd_info:
                for opt_name, opt_help in cmd_info["options"].items():
                    cmd_node.add(f"[option]{opt_name}[/option] [value]{opt_help}[/value]")
        
        # Config scope flags section
        flags_section = tree.add(f"[section]CONFIG SCOPE FLAGS[/section]")
        flags_section.add("[option]--global[/option]            [value]Use global configuration[/value]")
        flags_section.add("[option]--local[/option]             [value]Use local configuration[/value]")
        flags_section.add("[option]--file <PATH>[/option]       [value]Use named configuration file[/value]")
        
        # Global options section
        options_section = tree.add(f"[section]GLOBAL OPTIONS[/section]")
        options_section.add("[option]--help, -h[/option]          [value]Show help message[/value]")
        options_section.add("[option]--verbose, -v[/option]       [value]Enable verbose output[/value]")
        options_section.add("[option]--quiet, -q[/option]         [value]Suppress non-essential output[/value]")
        
        console.print(tree)
    
    @staticmethod
    def print_profile(profile: Dict[str, Any], name: str, profile_type: str = "LLM") -> None:
        """
        Print a profile with formatted output and color, masking sensitive fields.
        
        Args:
            profile: The profile data to display
            name: The name of the profile
            profile_type: The type of profile (default: "LLM")
        """
        title = Text()
        title.append(f"{profile_type} Profile: ", style="title")
        title.append(name, style="highlight")
        
        console.print(title)
        
        # Create a table for profile details
        table = Table(box=box.ROUNDED, show_header=True, header_style="header", border_style="blue")
        table.add_column("Property", style="key")
        table.add_column("Value", style="value")
        
        # Get sensitive field info
        sensitive_fields = []
        for key, param in [(p["name"], p) for p in getattr(profile, "_params", [])]:
            if param.get("sensitive", False):
                sensitive_fields.append(key)
        
        # Always consider api_key as sensitive
        if "api_key" not in sensitive_fields:
            sensitive_fields.append("api_key")
        
        # Special formatting for different property types
        for key, value in profile.items():
            if value is None:
                continue
                
            value_str = str(value)
            
            # Mask sensitive fields
            if key in sensitive_fields and value:
                # Keep first 4 and last 4 chars, mask the rest with asterisks
                if len(value_str) > 8:
                    value_str = value_str[:4] + "*" * (len(value_str) - 8) + value_str[-4:]
                else:
                    value_str = "********"  # For very short values
                value_style = "warning"
            # Color-code specific properties
            elif key == "name":
                value_style = "highlight"
            elif key == "provider":
                value_style = "subcommand"
            elif key == "model":
                value_style = "info"
            elif key == "temperature":
                value_style = "command"
            elif key == "max_tokens":
                value_style = "highlight"
            elif key in ["region", "project_id", "organization"]:
                value_style = "command"
            else:
                value_style = "value"
            
            table.add_row(key, f"[{value_style}]{value_str}[/{value_style}]")
        
        console.print(table)