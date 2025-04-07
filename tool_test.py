#!/usr/bin/env python3
"""
Simple script to test CLI functionality.
"""

import sys
import click
from cli_base.main import cli, initialize_settings

@click.group()
def test_cli():
    """Test runner for CLI commands."""
    pass

@test_cli.command()
@click.argument('command_args', nargs=-1)
def run(command_args):
    """
    Run a CLI command with arguments.
    
    Example: python tool_test.py run config show
    """
    # Enable settings
    initialize_settings()
    
    # Run the CLI with the provided arguments
    sys.argv = ['cli-tool'] + list(command_args)
    cli()

@test_cli.command()
@click.option('--folder', '-f', help='Output folder for the markdown file')
@click.option('--output', '-o', help='Output filename')
@click.option('--url', '-u', default='https://example.com', help='URL to fetch')
def test_get_page(folder, output, url):
    """
    Test the get-page command with a sample URL.
    
    Example: python tool_test.py test_get_page --url https://example.com --folder ./pages
    """
    # Enable settings
    initialize_settings()
    
    # Build arguments
    args = ['get-page', '--url', url]
    if folder:
        args.extend(['--folder', folder])
    if output:
        args.extend(['--output', output])
    
    # Run the command
    sys.argv = ['cli-tool'] + args
    try:
        cli()
        print("\nTest completed successfully!")
    except Exception as e:
        print(f"\nTest failed: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_cli()
    else:
        # Enable settings
        initialize_settings()
        
        # Run the CLI with the provided arguments
        cli(sys.argv[1:])