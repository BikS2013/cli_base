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
    
    # Combine file and output parameters (output is an alias for file)
    output_file = file or output
    
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
            
        # Function to process content using continuous generation approach
        def process_with_llm(content_to_process, need_filename=False):
            content_length = len(content_to_process)
            OutputFormatter.print_info(f"Processing content ({content_length} characters)...")
            
            # Initialize conversation
            messages = []
            
            # Step 1: Determine filename if needed
            suggested_filename = None
            if need_filename:
                filename_prompt = f"""
                You are tasked with converting raw text into well-formatted markdown.
                
                First, analyze this content and suggest an appropriate descriptive filename.
                Respond with a line starting with "FILENAME:" followed by your suggestion (e.g., "FILENAME: project-overview.md").
                
                After suggesting the filename, explain in 1-2 sentences why you chose it, but DO NOT start any conversion yet.
                
                Here's the content:
                {content_to_process[:min(2000, content_length)]}
                """
                
                OutputFormatter.print_info("Determining appropriate filename...")
                messages.append(HumanMessage(content=filename_prompt))
                first_response = llm.invoke(messages)
                
                # When verbose mode is enabled, output the raw model response
                if verbose:
                    OutputFormatter.print_verbose("Filename response from model:")
                    OutputFormatter.print_verbose("-" * 40)
                    OutputFormatter.print_verbose(first_response.content)
                    OutputFormatter.print_verbose("-" * 40)
                
                # Extract filename
                if "FILENAME:" in first_response.content[:200]:
                    lines = first_response.content.split('\n')
                    for line in lines[:3]:
                        if "FILENAME:" in line:
                            suggested_filename = line.split('FILENAME:')[1].strip()
                            OutputFormatter.print_info(f"Suggested filename: {suggested_filename}")
                            break
                
                # Add model's response to conversation
                messages.append(first_response)
            
            # Step 2: Start conversion process - always with the full content
            conversion_prompt = f"""
            Now I need you to convert the following content into well-formatted markdown.
            
            Guidelines:
            - Analyze the content carefully to determine its structure and purpose
            - Use appropriate headings, lists, tables, and formatting
            - Maintain the original information and hierarchy
            - Add appropriate markup like bold, italic, code blocks, etc. where it makes sense
            - Create a clean, professional document that preserves all important content
            
            I will ask you to continue generating if your response is incomplete.
            
            Here is the content to convert:
            
            {content_to_process}
            """
            
            messages.append(HumanMessage(content=conversion_prompt))
            OutputFormatter.print_info("Starting markdown conversion...")
            response = llm.invoke(messages)
            
            # When verbose mode is enabled, output the raw model response
            if verbose:
                OutputFormatter.print_verbose("Initial conversion response from model:")
                OutputFormatter.print_verbose("-" * 40)
                # Show beginning of response if very long
                preview_length = min(1000, len(response.content))
                OutputFormatter.print_verbose(response.content[:preview_length])
                if len(response.content) > preview_length:
                    OutputFormatter.print_verbose("... (response truncated in verbose output)")
                OutputFormatter.print_verbose("-" * 40)
            
            # Add model's response to conversation
            messages.append(response)
            
            # Initialize result content
            result_content = response.content
            
            # Step 3: Continue asking for more until the model indicates it's finished
            # We'll use a continuation counter and watch for signs of completion
            continuation_count = 0
            # Use the provided max_continuations parameter
            
            while continuation_count < max_continuations:
                continuation_count += 1
                
                # Check if the response seems complete
                last_paragraphs = response.content.strip().split('\n')[-3:]
                last_text = ' '.join(last_paragraphs).lower()
                
                # Detect completion signals
                completion_markers = [
                    "that concludes", "in conclusion", "this completes", 
                    "end of document", "# conclusion", "## conclusion",
                    "the end", "document end", "conversion complete"
                ]
                
                if any(marker in last_text for marker in completion_markers):
                    OutputFormatter.print_info("Conversion appears complete.")
                    break
                
                # Ask model to continue
                continuation_prompt = f"""
                Please continue where you left off. If you have completed the conversion, please say so explicitly.
                
                Remember to maintain the same formatting style and structure you established earlier.
                """
                
                OutputFormatter.print_info(f"Requesting continuation {continuation_count}...")
                messages.append(HumanMessage(content=continuation_prompt))
                response = llm.invoke(messages)
                
                # When verbose mode is enabled, output the raw model response
                if verbose:
                    OutputFormatter.print_verbose(f"Continuation {continuation_count} response:")
                    OutputFormatter.print_verbose("-" * 40)
                    # Show beginning of response if very long
                    preview_length = min(500, len(response.content))
                    OutputFormatter.print_verbose(response.content[:preview_length])
                    if len(response.content) > preview_length:
                        OutputFormatter.print_verbose("... (response truncated in verbose output)")
                    OutputFormatter.print_verbose("-" * 40)
                
                # Add to result content
                result_content += "\n\n" + response.content
                
                # Add model's response to conversation
                messages.append(response)
                
                # Manage conversation length - keep only recent messages
                if len(messages) > 6:
                    # Keep the first message (context) and the most recent exchanges
                    messages = [messages[0]] + messages[-5:]
            
            if continuation_count >= max_continuations:
                OutputFormatter.print_info("Reached maximum continuations - finalizing document.")
            
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
        
        # Print additional information in verbose mode
        if verbose:
            OutputFormatter.print_verbose("Processing Summary:")
            OutputFormatter.print_verbose(f"- Clipboard content size: {len(clipboard_content)} characters")
            OutputFormatter.print_verbose(f"- Output content size: {len(content)} characters")
            OutputFormatter.print_verbose(f"- Filename: {output_file}")
            OutputFormatter.print_verbose(f"- Saved to: {file_path}")
            if profile:
                OutputFormatter.print_verbose(f"- Used LLM profile: {profile}")
            else:
                OutputFormatter.print_verbose(f"- Used default LLM profile")
            
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