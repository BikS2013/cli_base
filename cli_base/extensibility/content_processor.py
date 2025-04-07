"""
Content processor for CLI tool.
Provides common functionality for processing content and converting it to formatted files.
"""

import os
import datetime
from typing import Optional, Dict, Any, List, Tuple, Callable

from cli_base.utils.profiles import BaseProfileManager
from cli_base.utils.formatting import OutputFormatter, console
from cli_base.utils.context import ContextManager
from cli_base.extensibility.llm_extension import get_llm_profile_manager
from langchain_core.messages import HumanMessage


class ContentProcessor:
    """
    Processes content from various sources and converts it to markdown using an LLM.
    
    This class provides common functionality used by both the get-clipboard and get-page commands.
    """
    
    def __init__(self, command_name: str, profile: Optional[str] = None, 
                 max_tokens: Optional[int] = None, temperature: Optional[float] = None,
                 max_continuations: int = 10, verbose: bool = False,
                 ctx: Optional[Any] = None):
        """
        Initialize the content processor with the provided parameters.
        
        Args:
            command_name: Name of the command using this processor (for config lookup)
            profile: LLM profile to use
            max_tokens: Override max tokens for this request
            temperature: Override temperature for this request
            max_continuations: Maximum number of continuations to request
            verbose: Whether to enable verbose output
            ctx: Context manager instance (if already initialized)
        """
        self.command_name = command_name
        self.profile_name = profile
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_continuations = max_continuations
        self.verbose = verbose
        self.ctx = ctx
        self.llm = None
        self.profile_data = None
        
        # Initialize LLM if profile is provided
        if profile:
            self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM with the profile settings."""
        try:
            # Get the profile manager
            profile_manager = get_llm_profile_manager()
            
            # If profile is not provided, use default
            if not self.profile_name:
                # Check if there's a default profile
                default_profile = profile_manager.get_default_profile()
                if not default_profile:
                    raise ValueError("No LLM profile specified and no default profile set.")
                self.profile_name = default_profile
                OutputFormatter.print_info(f"Using default profile: {self.profile_name}")
            
            # Get profile data - will throw error if not found
            self.profile_data = profile_manager.get_profile(self.profile_name)
            
            # Apply overrides if specified
            if self.max_tokens is not None:
                self.profile_data["max_tokens"] = self.max_tokens
            if self.temperature is not None:
                self.profile_data["temperature"] = self.temperature
            
            # Get the LLM
            self.llm = profile_manager.get_llm(self.profile_name)
            
            return True
        except ValueError as e:
            OutputFormatter.print_error(str(e))
            # Show available profiles
            profile_manager = get_llm_profile_manager()
            for scope in ["global", "local"]:
                try:
                    profiles = profile_manager.list_profiles(scope)
                    if profiles:
                        OutputFormatter.print_info(f"  {scope} profiles: {', '.join(profiles.keys())}")
                except Exception:
                    pass
            return False
        except Exception as e:
            OutputFormatter.print_error(f"Error initializing LLM: {str(e)}")
            return False
    
    def process_with_llm(self, content: str, metadata: Dict[str, str] = None, 
                         need_filename: bool = False) -> Tuple[str, Optional[str]]:
        """
        Process content using a continuous generation approach with the LLM.
        
        Args:
            content: The content to process
            metadata: Additional metadata to include in the prompt (e.g., title, source)
            need_filename: Whether to ask the LLM to suggest a filename
            
        Returns:
            Tuple of (processed_content, suggested_filename)
        """
        if not self.llm and not self._initialize_llm():
            return None, None
            
        content_length = len(content)
        OutputFormatter.print_info(f"Processing content ({content_length} characters)...")
        
        # Initialize conversation
        messages = []
        
        # Step 1: Determine filename if needed
        suggested_filename = None
        if need_filename:
            filename_prompt = self._get_filename_prompt(content, metadata)
            
            OutputFormatter.print_info("Determining appropriate filename...")
            messages.append(HumanMessage(content=filename_prompt))
            first_response = self.llm.invoke(messages)
            
            # When verbose mode is enabled, output the raw model response
            if self.verbose:
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
        conversion_prompt = self._get_conversion_prompt(content, metadata)
        
        messages.append(HumanMessage(content=conversion_prompt))
        OutputFormatter.print_info("Starting markdown conversion...")
        response = self.llm.invoke(messages)
        
        # When verbose mode is enabled, output the raw model response
        if self.verbose:
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
        
        while continuation_count < self.max_continuations:
            continuation_count += 1
            
            # Check if the response seems complete using a more robust detection
            last_paragraphs = response.content.strip().split('\n')[-5:]  # Check more lines
            last_text = ' '.join(last_paragraphs).lower()
            
            # Detect completion signals - more comprehensive list and check for variations
            completion_markers = [
                "that concludes", "in conclusion", "this completes", 
                "end of document", "# conclusion", "## conclusion",
                "the end", "document end", "conversion complete", "is complete",
                "has been completed", "is now complete", "complete.", "completed.", 
                "conversion is complete", "fully converted", "fully formatted",
                "finished", "all content has been", "all sections", 
                "all provided content", "complete conversion"
            ]
            
            # First, check for exact matches
            if any(marker in last_text for marker in completion_markers):
                OutputFormatter.print_info("Detected completion marker. Conversion finished.")
                break
                
            # Second, check for our explicit uppercase marker
            if "CONVERSION COMPLETE" in response.content:
                OutputFormatter.print_info("Explicit completion marker found. Conversion finished.")
                break
            
            # Third, check if "complete" appears with other keywords close by
            if "complete" in last_text and any(word in last_text for word in ["conversion", "all", "is", "now", "fully"]):
                OutputFormatter.print_info("Conversion appears complete.")
                break
            
            # Ask model to continue
            continuation_prompt = f"""
            Please continue where you left off. 
            
            IMPORTANT: If you've completed the conversion, say "CONVERSION COMPLETE" explicitly.
            
            Remember to maintain the same formatting style and structure you established earlier.
            """
            
            OutputFormatter.print_info(f"Requesting continuation {continuation_count}...")
            messages.append(HumanMessage(content=continuation_prompt))
            response = self.llm.invoke(messages)
            
            # When verbose mode is enabled, output the raw model response
            if self.verbose:
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
        
        if continuation_count >= self.max_continuations:
            OutputFormatter.print_info("Reached maximum continuations - finalizing document.")
        
        return result_content, suggested_filename
    
    def _get_filename_prompt(self, content: str, metadata: Dict[str, str] = None) -> str:
        """Generate the prompt for requesting a filename suggestion."""
        metadata = metadata or {}
        content_preview = content[:min(2000, len(content))]
        
        # Base prompt
        prompt = f"""
        You are tasked with converting content into well-formatted markdown.
        
        First, analyze this content and suggest an appropriate descriptive filename.
        Respond with a line starting with "FILENAME:" followed by your suggestion (e.g., "FILENAME: project-overview.md").
        
        After suggesting the filename, explain in 1-2 sentences why you chose it, but DO NOT start any conversion yet.
        """
        
        # Add metadata if available
        for key, value in metadata.items():
            prompt += f"\n{key}: {value}"
        
        # Add content preview
        prompt += f"""
        
        Here's the content:
        {content_preview}
        """
        
        return prompt
    
    def _get_conversion_prompt(self, content: str, metadata: Dict[str, str] = None) -> str:
        """Generate the prompt for content conversion."""
        metadata = metadata or {}
        
        # Base prompt
        prompt = f"""
        Now I need you to convert the following content into well-formatted markdown.
        
        Guidelines:
        - Analyze the content carefully to determine its structure and purpose
        - Use appropriate headings, lists, tables, and formatting
        - Maintain the original information and hierarchy
        - Add appropriate markup like bold, italic, code blocks, etc. where it makes sense
        - Create a clean, professional document that preserves all important content
        """
        
        # Add source-specific instructions
        if "source_type" in metadata:
            if metadata["source_type"] == "webpage":
                prompt += """
                - If this is a blog post or article, include the title as an H1 heading
                """
        
        # Add continuation instruction
        prompt += """
        
        I will ask you to continue generating if your response is incomplete.
        
        IMPORTANT: When you finish the conversion entirely, please explicitly state "CONVERSION COMPLETE" 
        at the end of your response so I know you've processed everything.
        """
        
        # Add metadata if available
        for key, value in metadata.items():
            if key != "source_type":  # Skip source_type as it's used for prompt customization
                prompt += f"\n{key}: {value}"
        
        # Add content
        prompt += f"""
        
        Here is the content to convert:
        
        {content}
        """
        
        return prompt
    
    def save_to_file(self, content: str, output_file: Optional[str], folder: str, 
                     suggested_filename: Optional[str] = None, default_prefix: str = "document",
                     metadata: Dict[str, Any] = None) -> str:
        """
        Save the processed content to a file.
        
        Args:
            content: Content to save
            output_file: User-specified output filename
            folder: Folder to save to
            suggested_filename: Filename suggested by the LLM
            default_prefix: Prefix to use for default filename if no name is provided
            metadata: Additional metadata to use for generating default filename
            
        Returns:
            The full path of the saved file
        """
        # Use suggested filename or output_file
        if not output_file and suggested_filename:
            output_file = suggested_filename
        
        # If still no filename, generate a timestamp-based one
        if not output_file:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # If we have metadata, use it to create a more descriptive filename
            if metadata and "title" in metadata:
                # Create a safe version of the title for the filename
                safe_title = "".join(c if c.isalnum() else "_" for c in metadata["title"])[:30]
                output_file = f"{safe_title}_{timestamp}.md"
            else:
                output_file = f"{default_prefix}_{timestamp}.md"
        
        # Ensure file has an extension if none provided
        if '.' not in output_file:
            output_file = f"{output_file}.md"
        
        # Handle output filename - if it contains a path, handle it appropriately
        if os.path.dirname(output_file):
            # If output_file contains a path, expand and resolve it
            output_dir = os.path.dirname(output_file)
            output_dir = os.path.expanduser(output_dir)
            output_dir = os.path.expandvars(output_dir)
            
            # If it's an absolute path, use it directly
            if os.path.isabs(output_dir):
                # Create the directory
                os.makedirs(output_dir, exist_ok=True)
                file_path = os.path.expanduser(output_file)
            else:
                # It's a relative path, combine with the folder
                output_dir = os.path.join(folder, output_dir)
                os.makedirs(output_dir, exist_ok=True)
                file_path = os.path.join(folder, output_file)
        else:
            # No path in the output_file, just use the folder
            file_path = os.path.join(folder, output_file)
        
        # Save content to file
        with open(file_path, 'w') as f:
            f.write(content)
        
        OutputFormatter.print_info(f"Successfully saved to: {file_path}")
        OutputFormatter.print_info(f"Content length: {len(content)} characters")
        
        if self.verbose:
            OutputFormatter.print_verbose(f"Full save path: {os.path.abspath(file_path)}")
        
        return file_path
    
    def process_content_to_markdown(self, content: str, folder: str, output_file: Optional[str] = None,
                                   metadata: Dict[str, Any] = None, default_prefix: str = "document") -> bool:
        """
        Process content and save it as a markdown file.
        
        Args:
            content: Content to process
            folder: Folder to save the file to
            output_file: Optional filename to use
            metadata: Additional metadata about the content
            default_prefix: Prefix to use for default filename
            
        Returns:
            True if processing succeeded, False otherwise
        """
        try:
            # Process content, requesting filename if not provided
            processed_content, suggested_filename = self.process_with_llm(
                content, 
                metadata=metadata, 
                need_filename=not output_file
            )
            
            if not processed_content:
                return False
            
            # Save the content to a file
            file_path = self.save_to_file(
                processed_content,
                output_file,
                folder,
                suggested_filename,
                default_prefix,
                metadata
            )
            
            # Print additional information in verbose mode
            if self.verbose:
                OutputFormatter.print_verbose("Processing Summary:")
                
                # Source info
                if "source_type" in metadata:
                    if metadata["source_type"] == "clipboard":
                        OutputFormatter.print_verbose(f"- Clipboard content size: {len(content)} characters")
                    elif metadata["source_type"] == "webpage":
                        OutputFormatter.print_verbose(f"- Web page content size: {len(content)} characters")
                        if "url" in metadata:
                            OutputFormatter.print_verbose(f"- Source URL: {metadata['url']}")
                        if "title" in metadata:
                            OutputFormatter.print_verbose(f"- Page title: {metadata['title']}")
                else:
                    OutputFormatter.print_verbose(f"- Source content size: {len(content)} characters")
                
                # Output info
                OutputFormatter.print_verbose(f"- Output content size: {len(processed_content)} characters")
                OutputFormatter.print_verbose(f"- Filename: {os.path.basename(file_path)}")
                OutputFormatter.print_verbose(f"- Saved to: {file_path}")
                
                # Model info
                if self.profile_name:
                    OutputFormatter.print_verbose(f"- Used LLM profile: {self.profile_name}")
                else:
                    OutputFormatter.print_verbose(f"- Used default LLM profile")
            
            return True
        except Exception as e:
            OutputFormatter.print_error(f"Error processing content: {str(e)}")
            return False
            
    @classmethod
    def get_folder_from_config(cls, command_name: str, folder: Optional[str] = None, ctx: Optional[Any] = None) -> str:
        """
        Get the folder to save to, checking command config if not specified.
        
        Args:
            command_name: Name of the command (for config lookup)
            folder: User-specified folder (may be None)
            ctx: Context manager instance (if already initialized)
            
        Returns:
            The folder path to use
        """
        # If context not provided, get it
        if not ctx:
            ctx = ContextManager.get_instance()
        
        rt_settings = ctx.settings
        cmd_config = rt_settings.get_command_config(command_name)
        
        if not folder:
            folder = cmd_config.get("folder", os.getcwd())
        
        # Expand any ~ or environment variables in the folder path
        folder = os.path.expanduser(folder)
        folder = os.path.expandvars(folder)
        
        # Convert to absolute path if it's a relative path
        if not os.path.isabs(folder):
            folder = os.path.abspath(folder)
            
        # Create folder if it doesn't exist
        os.makedirs(folder, exist_ok=True)
        
        # Check for verbose mode using the class variable
        if OutputFormatter.verbose_mode:
            OutputFormatter.print_verbose(f"Using folder: {folder}")
            
        return folder