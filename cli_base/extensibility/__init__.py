"""
Extensions requiring profile management and content processing functionality.

This package contains:
- Clipboard functionality for processing clipboard content
- Webpage functionality for processing web page content
- Common content processor for handling content from various sources
- LLM profile management extensions
"""

from cli_base.extensibility.clipboard_extension import get_clipboard_command
from cli_base.extensibility.webpage_extension import get_page_command
from cli_base.extensibility.content_processor import ContentProcessor