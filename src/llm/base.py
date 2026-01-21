"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def complete(self, prompt: str) -> str:
        """
        Send a prompt to the LLM and get a completion.
        
        Args:
            prompt: The prompt text to send
            
        Returns:
            The completion text from the LLM
        """
        pass
    
    @abstractmethod
    def complete_with_system(self, system: str, prompt: str) -> str:
        """
        Send a prompt with a system message to the LLM.
        
        Args:
            system: The system message/instructions
            prompt: The user prompt text
            
        Returns:
            The completion text from the LLM
        """
        pass
