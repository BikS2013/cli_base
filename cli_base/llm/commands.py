"""
LLM command module for using LLMs via the CLI.
Provides commands for sending prompts and generating content.
"""

import click
from typing import Optional

from cli_base.extensibility.llm_extension import get_llm_profile_manager
from cli_base.utils.formatting import OutputFormatter
from cli_base.utils.context import _initialize_context
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
def generate_prompt(prompt: str, profile: Optional[str] = None, stream: bool = True, 
                   max_tokens: Optional[int] = None, temperature: Optional[float] = None):
    """
    Generate a response from an LLM using the given prompt.
    
    Uses either the specified profile or the default profile.
    """
    # Initialize context
    _initialize_context({})
    
    try:
        # Get the profile manager
        profile_manager = get_llm_profile_manager()
        
        # Get profile name to use
        if not profile:
            default_profile = profile_manager.get_default_profile()
            if not default_profile:
                OutputFormatter.print_error("No LLM profile specified and no default profile set.")
                OutputFormatter.print_info("Use: cli-tool llm use <profile-name> to set a default")
                return
            profile = default_profile
            OutputFormatter.print_info(f"Using default profile: {profile}")
        
        # Get the profile data
        profile_data = profile_manager.get_profile(profile)
        if not profile_data:
            OutputFormatter.print_error(f"Profile '{profile}' not found.")
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
def interactive_chat(profile: Optional[str] = None):
    """
    Start an interactive chat session with an LLM.
    
    Press Ctrl+D or type 'exit' to end the session.
    """
    # Initialize context
    _initialize_context({})
    
    try:
        # Get the profile manager
        profile_manager = get_llm_profile_manager()
        
        # Get profile name to use
        if not profile:
            default_profile = profile_manager.get_default_profile()
            if not default_profile:
                OutputFormatter.print_error("No LLM profile specified and no default profile set.")
                OutputFormatter.print_info("Use: cli-tool llm use <profile-name> to set a default")
                return
            profile = default_profile
            OutputFormatter.print_info(f"Using default profile: {profile}")
        
        # Get the LLM
        llm = profile_manager.get_llm(profile)
        
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