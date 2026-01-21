"""Anthropic Claude LLM provider implementation."""

import anthropic

from .base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize the Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            model: Model name to use (default: claude-sonnet-4-20250514)
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def complete(self, prompt: str) -> str:
        """
        Send a prompt to Claude and get a completion.
        
        Args:
            prompt: The prompt text to send
            
        Returns:
            The completion text from Claude
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    
    def complete_with_system(self, system: str, prompt: str) -> str:
        """
        Send a prompt with a system message to Claude.
        
        Args:
            system: The system message/instructions
            prompt: The user prompt text
            
        Returns:
            The completion text from Claude
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
