"""
LLM command module for using LLMs via the CLI.
Provides commands for sending prompts and generating content.
"""

import click
from typing import Optional

from cli_base.extensibility.llm_extension import get_llm_profile_manager
from cli_base.utils.formatting import OutputFormatter
from cli_base.utils.context import ContextManager, initialize_context
from cli_base.utils.advanced_settings import get_parameter_value
from cli_base.utils.param_resolver import with_resolved_params
from cli_base.commands.cmd_options import scope_options
from langchain_core.messages import HumanMessage

@click.group("generate")
def generate_group():
    """Generate content using LLM models."""
    pass

@generate_group.command("prompt")
@click.argument("prompt", type=str)
@click.option("--profile", "-p", help="LLM profile to use (uses default if not specified)")
@click.option("--stream/--no-stream", default=True, help="Stream the response (default: True)")
@click.option("--max-tokens", type=int, help="Override max tokens for this request")
@click.option("--temperature", type=float, help="Override temperature for this request")
@scope_options
@with_resolved_params
def generate_prompt(prompt: str, profile: Optional[str] = None, stream: bool = True, 
                   max_tokens: Optional[int] = None, temperature: Optional[float] = None,
                   scope: Optional[str] = None, file_path: Optional[str] = None):
    """
    Generate a response from an LLM using the given prompt.
    
    Uses either the specified profile or the default profile.
    """
    # Initialize context if not already initialized
    try:
        scope_params = {"scope": scope, "file_path": file_path}
        initialize_context(scope_params)
    except Exception as e:
        OutputFormatter.print_error(f"Error initializing context: {str(e)}")
    
    try:
        # Get the profile manager
        profile_manager = get_llm_profile_manager()
        
        # Profile parameter is automatically resolved by @with_resolved_params
        # If not provided, it will automatically use the default profile
        
        if not profile:
            # Check if there's a default profile
            default_profile = profile_manager.get_default_profile()
            if not default_profile:
                OutputFormatter.print_error("No LLM profile specified and no default profile set.")
                OutputFormatter.print_info("Use: cli-tool llm create <name> --provider <provider> --model <model> --api-key <key> to create a profile")
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

@generate_group.command("chat")
@click.option("--profile", "-p", help="LLM profile to use (uses default if not specified)")
@scope_options
@with_resolved_params
def interactive_chat(profile: Optional[str] = None, scope: Optional[str] = None, file_path: Optional[str] = None):
    """
    Start an interactive chat session with an LLM.
    
    Press Ctrl+D or type 'exit' to end the session.
    """
    # Initialize context
    try:
        scope_params = {"scope": scope, "file_path": file_path}
        initialize_context(scope_params)
    except Exception as e:
        OutputFormatter.print_error(f"Error initializing context: {str(e)}")
    
    try:
        # Get the profile manager
        profile_manager = get_llm_profile_manager()
        
        # Check if profile is provided or there's a default
        if not profile:
            default_profile = profile_manager.get_default_profile()
            if not default_profile:
                OutputFormatter.print_error("No LLM profile specified and no default profile set.")
                OutputFormatter.print_info("Use: cli-tool llm create <name> --provider <provider> --model <model> --api-key <key> to create a profile")
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
        
        # Keep track of messages for context
        messages = []
        
        while True:
            # Get user input
            try:
                user_input = click.prompt("\n[bold green]You[/bold green]", prompt_suffix="\n")
                if user_input.lower() in ["exit", "quit", "bye"]:
                    break
            except (EOFError, KeyboardInterrupt):
                click.echo("\nExiting chat session.")
                break
            
            # Add user message to history
            messages.append(HumanMessage(content=user_input))
            
            # Print assistant response
            click.echo("\n[bold blue]Assistant[/bold blue]")
            response_content = ""
            
            # Stream the response
            for chunk in llm.stream(messages):
                content = chunk.content
                if content:
                    print(content, end="", flush=True)
                    response_content += content
            print()  # Add final newline
            
            # Add assistant response to history
            from langchain_core.messages import AIMessage
            messages.append(AIMessage(content=response_content))
            
    except ImportError as e:
        OutputFormatter.print_error(f"LangChain not installed: {str(e)}")
        OutputFormatter.print_info("Install LangChain with: pip install langchain-core langchain-openai")
    except Exception as e:
        OutputFormatter.print_error(f"Error: {str(e)}")

# Export the command group
generate_command = generate_group