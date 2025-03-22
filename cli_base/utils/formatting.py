"""
Formatting utilities for CLI tool output.
Provides colorful and structured terminal output.
"""

from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich import box
from typing import Dict, List, Any, Optional, Union

console = Console()

class OutputFormatter:
    """Formats CLI output with color and structure."""
    
    @staticmethod
    def print_success(message: str) -> None:
        """Print a success message in green."""
        console.print(f"[green]{message}[/green]")
    
    @staticmethod
    def print_warning(message: str) -> None:
        """Print a warning message in yellow."""
        console.print(f"[yellow]{message}[/yellow]")
    
    @staticmethod
    def print_error(message: str) -> None:
        """Print an error message in red."""
        console.print(f"[red]{message}[/red]")
    
    @staticmethod
    def print_info(message: str) -> None:
        """Print an informational message in blue."""
        console.print(f"[blue]{message}[/blue]")
    
    @staticmethod
    def print_json(data: Dict[str, Any], title: Optional[str] = None) -> None:
        """Print data as formatted JSON."""
        if title:
            console.print(f"[bold]{title}[/bold]")
        console.print_json(data=data)
    
    @staticmethod
    def print_table(
        data: List[Dict[str, Any]], 
        columns: List[str], 
        title: Optional[str] = None,
        box_style: box.Box = box.ROUNDED
    ) -> None:
        """Print data as a table."""
        table = Table(title=title, box=box_style, show_header=True, header_style="bold")
        
        # Add columns
        for column in columns:
            table.add_column(column)
        
        # Add rows
        for row in data:
            table.add_row(*[str(row.get(col, "")) for col in columns])
        
        console.print(table)
    
    @staticmethod
    def print_tree(
        tree_data: Dict[str, Any], 
        title: str = "Command Structure",
        show_values: bool = True
    ) -> None:
        """Print a hierarchical tree structure."""
        tree = Tree(f"[bright_cyan]{title}[/bright_cyan]")
        
        def add_nodes(parent, data):
            for key, value in data.items():
                if isinstance(value, dict):
                    node = parent.add(f"[cyan]{key}[/cyan]")
                    add_nodes(node, value)
                elif isinstance(value, list):
                    node = parent.add(f"[blue]{key}[/blue]")
                    for item in value:
                        if isinstance(item, dict):
                            subnode = node.add(f"[green]{item.get('name', 'Item')}[/green]")
                            for k, v in item.items():
                                if k != 'name' and show_values:
                                    subnode.add(f"[white]{k}: {v}[/white]")
                        else:
                            node.add(f"[white]{item}[/white]")
                elif show_values:
                    parent.add(f"[green]{key}:[/green] [white]{value}[/white]")
        
        add_nodes(tree, tree_data)
        console.print(tree)
    
    @staticmethod
    def print_command_tree(commands: Dict[str, Any]) -> None:
        """Print a formatted command tree structure."""
        tree = Tree("[bright_cyan]cli-tool[/bright_cyan]")
        
        # Commands section
        cmd_section = tree.add("[yellow]COMMANDS[/yellow]")
        for cmd_name, cmd_info in commands.items():
            cmd_node = cmd_section.add(f"[cyan]{cmd_name}[/cyan]                [white]{cmd_info.get('help', '')}[/white]")
            
            # Add subcommands if any
            if "subcommands" in cmd_info:
                for subcmd_name, subcmd_info in cmd_info["subcommands"].items():
                    subcmd_node = cmd_node.add(f"[blue]{subcmd_name}[/blue]            [white]{subcmd_info.get('help', '')}[/white]")
                    
                    # Add options if any
                    if "options" in subcmd_info:
                        for opt_name, opt_help in subcmd_info["options"].items():
                            subcmd_node.add(f"[green]{opt_name}[/green] [white]{opt_help}[/white]")
        
        # Config scope flags section
        flags_section = tree.add("[yellow]CONFIG SCOPE FLAGS[/yellow]")
        flags_section.add("[green]--global[/green]            [white]Use global configuration[/white]")
        flags_section.add("[green]--local[/green]             [white]Use local configuration[/white]")
        flags_section.add("[green]--file <PATH>[/green]       [white]Use named configuration file[/white]")
        
        # Global options section
        options_section = tree.add("[yellow]GLOBAL OPTIONS[/yellow]")
        options_section.add("[green]--help, -h[/green]          [white]Show help message[/white]")
        options_section.add("[green]--verbose, -v[/green]       [white]Enable verbose output[/white]")
        options_section.add("[green]--quiet, -q[/green]         [white]Suppress non-essential output[/white]")
        
        console.print(tree)