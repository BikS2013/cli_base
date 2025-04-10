"""
Clipboard extension for CLI tool.
Provides the get-clipboard command for converting clipboard content to formatted files.
"""

import click
import os
from typing import Optional, Dict, Any, List

from cli_base.utils.formatting import OutputFormatter
from cli_base.utils.context import ContextManager
from cli_base.commands.cmd_options import scope_options
from cli_base.extensibility.content_processor import ContentProcessor


@click.command("get-clipboard")
@click.option("--folder", "-f", help="Folder where to save the file (uses current folder if not specified)")
@click.option("--file", "--output", "-o", help="Name of the file to save (LLM will decide if not specified)")
@click.option("--profile", "-p", help="LLM profile to use (uses default if not specified)")
@click.option("--max-tokens", type=int, help="Override max tokens for this request")
@click.option("--temperature", type=float, help="Override temperature for this request")
@click.option("--max-continuations", type=int, default=10, help="Maximum number of continuations to request")
@scope_options
def get_clipboard_command(folder: Optional[str] = None, file: Optional[str] = None, output: Optional[str] = None,
                           profile: Optional[str] = None, max_tokens: Optional[int] = None, 
                           temperature: Optional[float] = None, max_continuations: int = 10,
                           scope: Optional[str] = None, file_path: Optional[str] = None):
    """
    Convert clipboard content to a markdown file using an LLM.
    
    Reads content from the clipboard, asks an LLM to convert it to well-formatted markdown,
    and saves the result to a file. If no folder is specified, the current folder is used.
    If no filename is specified (via --file or --output), the LLM will suggest an appropriate filename.
    
    Uses a conversational approach that sends the entire content to the LLM and then 
    continuously asks for more output until the document is complete. This maintains full context 
    throughout the conversation and creates a coherent, well-structured document.
    
    Run with --verbose (-v) to see detailed output including the raw model responses
    at each stage of processing.
    """
    # Initialize context
    ctx = ContextManager.initialize({"scope": scope, "file_path": file_path})
    
    # Detect verbose mode and set it
    verbose = OutputFormatter.detect_verbose_mode()
    
    # Initialize context and get command config
    rt_settings = ctx.settings
    cmd_config = rt_settings.get_command_config("get-clipboard")
    
    # Combine file and output parameters (output is an alias for file)
    output_file = file or output
    
    # Get config defaults if parameters not specified
    if not profile:
        profile = cmd_config.get("profile")
    if max_tokens is None and "max_tokens" in cmd_config:
        max_tokens = cmd_config.get("max_tokens")
    if temperature is None and "temperature" in cmd_config:
        temperature = cmd_config.get("temperature")
    if max_continuations == 10 and "max_continuations" in cmd_config:
        max_continuations = cmd_config.get("max_continuations")
    
    # Print verbose information if enabled
    OutputFormatter.print_command_verbose_info("get-clipboard",
                                          folder=folder,
                                          output=output_file,
                                          profile=profile,
                                          max_tokens=max_tokens,
                                          temperature=temperature,
                                          max_continuations=max_continuations,
                                          scope=scope,
                                          file_path=file_path)
                                         
    if verbose and cmd_config:
        OutputFormatter.print_verbose("Using command config:")
        for key, value in cmd_config.items():
            OutputFormatter.print_verbose(f"  {key}: {value}")
    
    try:
        # Import pyperclip here to avoid import errors at module level
        try:
            import pyperclip
        except ImportError:
            OutputFormatter.print_error("Pyperclip not installed. Please install it with: pip install pyperclip")
            return
        
        # Get clipboard content
        try:
            clipboard_content = pyperclip.paste()
            if not clipboard_content:
                OutputFormatter.print_error("Clipboard is empty. Copy some content first.")
                return
            OutputFormatter.print_info(f"Found {len(clipboard_content)} characters in clipboard")
        except Exception as e:
            OutputFormatter.print_error(f"Could not read clipboard: {str(e)}")
            return
        
        # Create the content processor
        processor = ContentProcessor(
            command_name="get-clipboard",
            profile=profile,
            max_tokens=max_tokens,
            temperature=temperature,
            max_continuations=max_continuations,
            verbose=verbose,
            ctx=ctx
        )
        
        # Get the folder to save to
        folder = ContentProcessor.get_folder_from_config("get-clipboard", folder, ctx)
        
        # Process the content
        OutputFormatter.print_info("Processing clipboard content with LLM...\n")
        
        # Create metadata dictionary
        metadata = {
            "source_type": "clipboard"
        }
        
        # Process content and save to file
        success = processor.process_content_to_markdown(
            content=clipboard_content,
            folder=folder,
            output_file=output_file,
            metadata=metadata,
            default_prefix="document"
        )
        
        if not success:
            return
            
    except ImportError as e:
        if "langchain" in str(e).lower():
            OutputFormatter.print_error(f"LangChain not installed: {str(e)}")
            OutputFormatter.print_info("Install LangChain with: pip install langchain-core langchain-openai")
        else:
            OutputFormatter.print_error(f"Required library not installed: {str(e)}")
    except Exception as e:
        OutputFormatter.print_error(f"Error: {str(e)}")
    
    # Print runtime settings at the end if verbose mode is enabled
    if verbose:
        OutputFormatter.end_command_with_runtime_settings(include_configs=False)