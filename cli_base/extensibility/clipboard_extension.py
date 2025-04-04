"""
Clipboard extension for CLI tool.
Provides the get-clipboard command for converting clipboard content to formatted files.
"""

import click
import os
import datetime
from typing import Optional, Dict, Any, List

from cli_base.utils.profiles import BaseProfileManager
from cli_base.utils.formatting import OutputFormatter, console
from cli_base.utils.context import ContextManager
from cli_base.commands.cmd_options import scope_options
from cli_base.extensibility.llm_extension import get_llm_profile_manager
from langchain_core.messages import HumanMessage


@click.command("get-clipboard")
@click.option("--folder", "-f", help="Folder where to save the file (uses current folder if not specified)")
@click.option("--file", "--output", "-o", help="Name of the file to save (LLM will decide if not specified)")
@click.option("--profile", "-p", help="LLM profile to use (uses default if not specified)")
@click.option("--max-tokens", type=int, help="Override max tokens for this request")
@click.option("--temperature", type=float, help="Override temperature for this request")
@click.option("--chunk-size", type=int, default=5000, help="Break input into chunks of this size for large content")
@scope_options
def get_clipboard_command(folder: Optional[str] = None, file: Optional[str] = None, output: Optional[str] = None,
                           profile: Optional[str] = None, max_tokens: Optional[int] = None, 
                           temperature: Optional[float] = None, chunk_size: int = 5000,
                           scope: Optional[str] = None, file_path: Optional[str] = None):
    """
    Convert clipboard content to a markup file using an LLM.
    
    Reads content from the clipboard, asks an LLM to convert it to appropriate markup,
    and saves the result to a file. If no folder is specified, the current folder is used.
    If no filename is specified (via --file or --output), the LLM will suggest an appropriate filename.
    
    For large clipboard content, the command will process it in chunks to avoid token limits.
    """
    # Initialize context
    ctx = ContextManager.initialize({"scope": scope, "file_path": file_path})
    
    # Detect verbose mode and set it
    verbose = OutputFormatter.detect_verbose_mode()
    
    # Combine file and output parameters (output is an alias for file)
    output_file = file or output
    
    # Print verbose information if enabled
    OutputFormatter.print_command_verbose_info("from-clipboard",
                                             folder=folder,
                                             output=output_file,
                                             profile=profile,
                                             max_tokens=max_tokens,
                                             temperature=temperature,
                                             chunk_size=chunk_size,
                                             scope=scope,
                                             file_path=file_path)
    
    try:
        # Import pyperclip here to avoid import errors at module level
        try:
            import pyperclip
        except ImportError:
            OutputFormatter.print_error("Pyperclip not installed. Please install it with: pip install pyperclip")
            return
            
        # Get the profile manager
        profile_manager = get_llm_profile_manager()
        
        # If profile is not provided, use default
        if not profile:
            # Check if there's a default profile
            default_profile = profile_manager.get_default_profile()
            if not default_profile:
                OutputFormatter.print_error("No LLM profile specified and no default profile set.")
                OutputFormatter.print_info("Use: cli-tool llm create <n> --provider <provider> --model <model> --api-key <key> to create a profile")
                OutputFormatter.print_info("Then use: cli-tool llm use <profile-name> to set it as default")
                return
            profile = default_profile
            OutputFormatter.print_info(f"Using default profile: {profile}")
        
        # Get profile data - will throw error if not found
        try:
            profile_data = profile_manager.get_profile(profile)
        except ValueError:
            OutputFormatter.print_error(f"Profile '{profile}' not found.")
            # Show available profiles
            for scope in ["global", "local"]:
                try:
                    profiles = profile_manager.list_profiles(scope)
                    if profiles:
                        OutputFormatter.print_info(f"  {scope} profiles: {', '.join(profiles.keys())}")
                except Exception:
                    pass
            return
        
        # Apply overrides if specified
        if max_tokens is not None:
            profile_data["max_tokens"] = max_tokens
        if temperature is not None:
            profile_data["temperature"] = temperature
        
        # Get the LLM
        llm = profile_manager.get_llm(profile)
        
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
        
        # Set folder to current directory if not specified
        if not folder:
            folder = os.getcwd()
        else:
            # Create folder if it doesn't exist
            os.makedirs(folder, exist_ok=True)
            
        # Function to process content in chunks if needed
        def process_with_llm(content_to_process, need_filename=False):
            # For large content, determine if we need to chunk
            content_length = len(content_to_process)
            
            if content_length > chunk_size:
                OutputFormatter.print_info(f"Content is large ({content_length} chars), processing in chunks...")
                
                # First, process a small piece to get the filename if needed
                first_chunk = content_to_process[:min(1000, content_length)]
                filename_prompt = f"""
                I have raw content that needs to be converted to a well-formatted markup document.
                This is just a sample of the beginning of the content for you to understand its nature.
                
                {'Please suggest an appropriate filename for this content at the beginning of your response in the format FILENAME: example.md' if need_filename else ''}
                
                Here's the beginning of the content:
                {first_chunk}
                """
                
                # Get filename from first chunk if needed
                if need_filename:
                    first_response = llm.invoke([HumanMessage(content=filename_prompt)])
                    suggested_filename = None
                    
                    # Extract filename
                    if "FILENAME:" in first_response.content[:200]:
                        lines = first_response.content.split('\n')
                        for line in lines[:3]:
                            if "FILENAME:" in line:
                                suggested_filename = line.split('FILENAME:')[1].strip()
                                break
                
                # Process content in chunks
                chunks = [content_to_process[i:i+chunk_size] for i in range(0, content_length, chunk_size)]
                full_result = ""
                
                for i, chunk in enumerate(chunks):
                    chunk_prompt = f"""
                    This is chunk {i+1} of {len(chunks)} from a larger document that needs to be converted to markup.
                    {'You already suggested a filename in an earlier chunk, so no need to do that again.' if need_filename and i > 0 else ''}
                    
                    Please convert ONLY this chunk to appropriate markup format. I will combine all chunks later.
                    
                    Here's the content for this chunk:
                    {chunk}
                    """
                    
                    OutputFormatter.print_info(f"Processing chunk {i+1}/{len(chunks)}...")
                    chunk_response = llm.invoke([HumanMessage(content=chunk_prompt)])
                    full_result += chunk_response.content + "\n\n"
                
                return full_result, suggested_filename if need_filename else None
            else:
                # Process content normally for smaller content
                prompt = f"""
                I have raw content that needs to be converted to a well-formatted markup document.
                Please convert this content to the most appropriate markup format (Markdown, reStructuredText, etc.)
                based on the content type. Ensure proper headings, lists, and formatting are applied.
                
                {'' if not need_filename else 'Also, suggest an appropriate filename for this content at the beginning of your response in the format FILENAME: example.md'}
                
                Here's the content:
                {content_to_process}
                """
                
                # Get response
                response = llm.invoke([HumanMessage(content=prompt)])
                result_content = response.content
                
                # Extract filename if requested
                suggested_filename = None
                if need_filename and "FILENAME:" in result_content[:200]:
                    lines = result_content.split('\n')
                    for line in lines[:3]:  # Check first few lines
                        if "FILENAME:" in line:
                            suggested_filename = line.split('FILENAME:')[1].strip()
                            # Remove the filename line from the content
                            result_content = '\n'.join([l for l in lines if "FILENAME:" not in l])
                            break
                
                return result_content, suggested_filename
        
        OutputFormatter.print_info("Processing clipboard content with LLM...\n")
        
        # Process content, requesting filename if not provided
        content, suggested_filename = process_with_llm(clipboard_content, need_filename=not output_file)
        
        # Use suggested filename or output_file
        if not output_file and suggested_filename:
            output_file = suggested_filename
        
        # If still no filename, generate a timestamp-based one
        if not output_file:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"document_{timestamp}.md"
        
        # Ensure file has an extension if none provided
        if '.' not in output_file:
            output_file = f"{output_file}.md"
        
        # Create full file path
        file_path = os.path.join(folder, output_file)
        
        # Save content to file
        with open(file_path, 'w') as f:
            f.write(content)
        
        OutputFormatter.print_info(f"Successfully saved to: {file_path}")
        OutputFormatter.print_info(f"Content length: {len(content)} characters")
            
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