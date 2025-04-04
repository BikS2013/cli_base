"""
LLM command module for using LLMs via the CLI.
Provides commands for asking questions and engaging in chat sessions.
"""

import click
import readline
import os
from typing import Optional

from cli_base.extensibility.llm_extension import get_llm_profile_manager
from cli_base.utils.formatting import OutputFormatter, console
from cli_base.utils.context import ContextManager, initialize_context
from cli_base.commands.cmd_options import scope_options
from langchain_core.messages import HumanMessage, AIMessage

@click.command("ask")
@click.argument("prompt", type=str)
@click.option("--profile", "-p", help="LLM profile to use (uses default if not specified)")
@click.option("--stream/--no-stream", default=True, help="Stream the response (default: True)")
@click.option("--max-tokens", type=int, help="Override max tokens for this request")
@click.option("--temperature", type=float, help="Override temperature for this request")
@scope_options
def ask_command(prompt: str, profile: Optional[str] = None, stream: bool = True, 
               max_tokens: Optional[int] = None, temperature: Optional[float] = None,
               scope: Optional[str] = None, file_path: Optional[str] = None):
    """
    Ask a question to an LLM and get a response.
    
    Uses either the specified profile or the default profile.
    """
    # Initialize context
    ctx = ContextManager.initialize({"scope": scope, "file_path": file_path})
    
    # Detect verbose mode and set it
    verbose = OutputFormatter.detect_verbose_mode()
    
    # Print verbose information if enabled
    OutputFormatter.print_command_verbose_info("ask", 
                                             prompt=prompt,
                                             profile=profile,
                                             stream=stream,
                                             max_tokens=max_tokens,
                                             temperature=temperature,
                                             scope=scope,
                                             file_path=file_path)
    
    try:
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
        
        # Send the prompt and get response
        OutputFormatter.print_info("Sending prompt to LLM...\n")
        
        if stream:
            # Stream the response
            for chunk in llm.stream([HumanMessage(content=prompt)]):
                content = chunk.content
                if content:
                    print(content, end="", flush=True)
            print()  # Add final newline
        else:
            # Get complete response
            response = llm.invoke([HumanMessage(content=prompt)])
            click.echo(response.content)
            
    except ImportError as e:
        OutputFormatter.print_error(f"LangChain not installed: {str(e)}")
        OutputFormatter.print_info("Install LangChain with: pip install langchain-core langchain-openai")
    except Exception as e:
        OutputFormatter.print_error(f"Error: {str(e)}")
    
    # Print runtime settings at the end if verbose mode is enabled
    if verbose:
        OutputFormatter.end_command_with_runtime_settings(include_configs=False)

@click.command("chat")
@click.option("--profile", "-p", help="LLM profile to use (uses default if not specified)")
@scope_options
def chat_command(profile: Optional[str] = None, scope: Optional[str] = None, file_path: Optional[str] = None):
    """
    Start an interactive chat session with an LLM.
    
    Press Ctrl+D or type 'exit' to end the session.
    """
    # Initialize context
    ctx = ContextManager.initialize({"scope": scope, "file_path": file_path})
    
    # Detect verbose mode and set it
    verbose = OutputFormatter.detect_verbose_mode()
    
    # Print verbose information if enabled
    OutputFormatter.print_command_verbose_info("chat",
                                           profile=profile,
                                           scope=scope,
                                           file_path=file_path)
    
    try:
        # Get the profile manager
        profile_manager = get_llm_profile_manager()
        
        # Check if profile is provided or there's a default
        if not profile:
            default_profile = profile_manager.get_default_profile()
            if not default_profile:
                OutputFormatter.print_error("No LLM profile specified and no default profile set.")
                OutputFormatter.print_info("Use: cli-tool llm create <n> --provider <provider> --model <model> --api-key <key> to create a profile")
                OutputFormatter.print_info("Then use: cli-tool llm use <profile-name> to set it as default")
                return
            profile = default_profile
            OutputFormatter.print_info(f"Using default profile: {profile}")
        
        try:
            # Get the LLM
            llm = profile_manager.get_llm(profile)
        except ValueError as e:
            OutputFormatter.print_error(str(e))
            OutputFormatter.print_info("Available profiles:")
            
            # Show available profiles
            for scope in ["global", "local"]:
                try:
                    profiles = profile_manager.list_profiles(scope)
                    if profiles:
                        OutputFormatter.print_info(f"  {scope} profiles: {', '.join(profiles.keys())}")
                except Exception:
                    pass
            return
        
        # Start chat session
        OutputFormatter.print_info("Starting chat session (press Ctrl+D or type 'exit' to end)")
        OutputFormatter.print_info("Model: " + profile_manager.get_profile(profile).get("model", "Unknown"))
        
        # Set up readline with history file for input persistence
        history_file = os.path.expanduser("~/.cli_tool_chat_history")
        try:
            # Create history file if it doesn't exist
            if not os.path.exists(history_file):
                with open(history_file, 'w') as f:
                    pass
                
            # Load history from file
            readline.read_history_file(history_file)
            # Set history length
            readline.set_history_length(1000)
        except Exception as e:
            # Handle potential readline errors gracefully
            if verbose:
                OutputFormatter.print_warning(f"Could not set up readline history: {str(e)}")
        
        # Set up tab completion
        def complete(text, state):
            # Simple completion of common commands
            commands = ['exit', 'quit', 'bye', 'help', 'clear']
            matches = [cmd for cmd in commands if cmd.startswith(text)]
            return matches[state] if state < len(matches) else None
            
        readline.set_completer(complete)
        readline.parse_and_bind("tab: complete")
        
        # Keep track of messages for context
        messages = []
        
        # Display initial instruction
        console.print("[dim]Type your messages below. Use arrow keys to navigate, Ctrl+A/E to jump to start/end.[/dim]")
        console.print("[dim]Tab completion available for commands. History is saved between sessions.[/dim]")
        console.print("[dim]Type 'exit', 'quit', or 'bye' to end the session.[/dim]")
        
        while True:
            # Get user input
            try:
                # Use Rich formatting for the prompt
                console.print("\n[bold green]You[/bold green]", end="")
                user_input = input("\n")
                
                # Add valid input to history
                if user_input.strip() and user_input.lower() not in ['exit', 'quit', 'bye']:
                    readline.add_history(user_input)
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    break
                
                # Special command: help
                if user_input.lower() == "help":
                    console.print("[dim]Commands:[/dim]")
                    console.print("[dim]  help - Show this help message[/dim]")
                    console.print("[dim]  exit/quit/bye - End the session[/dim]")
                    console.print("[dim]  clear - Clear the screen[/dim]")
                    console.print("[dim]Navigation:[/dim]")
                    console.print("[dim]  Arrow keys - Navigate through text/history[/dim]")
                    console.print("[dim]  Ctrl+A - Jump to start of line[/dim]")
                    console.print("[dim]  Ctrl+E - Jump to end of line[/dim]")
                    console.print("[dim]  Ctrl+L - Clear screen[/dim]")
                    console.print("[dim]  Tab - Auto-complete commands[/dim]")
                    continue
                
                # Special command: clear screen
                if user_input.lower() == "clear":
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                
            except (EOFError, KeyboardInterrupt):
                console.print("\nExiting chat session.")
                break
            
            # Save history to file
            try:
                readline.write_history_file(history_file)
            except Exception:
                pass
                
            # Add user message to history
            messages.append(HumanMessage(content=user_input))
            
            # Print assistant response using Rich
            console.print("\n[bold blue]Assistant[/bold blue]", end="")
            console.print()  # Add a new line
            response_content = ""
            
            # Stream the response
            for chunk in llm.stream(messages):
                content = chunk.content
                if content:
                    print(content, end="", flush=True)
                    response_content += content
            print()  # Add final newline
            
            # Add assistant response to history
            messages.append(AIMessage(content=response_content))
            
    except ImportError as e:
        OutputFormatter.print_error(f"LangChain not installed: {str(e)}")
        OutputFormatter.print_info("Install LangChain with: pip install langchain-core langchain-openai")
    except Exception as e:
        OutputFormatter.print_error(f"Error: {str(e)}")
    
    # Print runtime settings at the end if verbose mode is enabled
    if verbose:
        OutputFormatter.end_command_with_runtime_settings(include_configs=False)