"""OpenAI LLM provider implementation."""

from openai import OpenAI

from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name to use (default: gpt-4o)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def complete(self, prompt: str) -> str:
        """
        Send a prompt to OpenAI and get a completion.
        
        Args:
            prompt: The prompt text to send
            
        Returns:
            The completion text from OpenAI
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    
    def complete_with_system(self, system: str, prompt: str) -> str:
        """
        Send a prompt with a system message to OpenAI.
        
        Args:
            system: The system message/instructions
            prompt: The user prompt text
            
        Returns:
            The completion text from OpenAI
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
