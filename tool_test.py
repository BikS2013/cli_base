#!/usr/bin/env python3
"""
Simple script to test CLI functionality.
"""

import sys
from cli_base.main import cli, initialize_settings

if __name__ == '__main__':
    # Enable settings
    initialize_settings()
    
    # Run the CLI with the provided arguments
    cli(sys.argv[1:])