"""Ollama local LLM provider implementation."""

import json
import urllib.request
import urllib.error

from .base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        """
        Initialize the Ollama provider.
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use (default: llama3)
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
    
    def complete(self, prompt: str) -> str:
        """
        Send a prompt to Ollama and get a completion.
        
        Args:
            prompt: The prompt text to send
            
        Returns:
            The completion text from Ollama
        """
        url = f"{self.base_url}/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(request) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("response", "")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Failed to connect to Ollama at {self.base_url}: {e}")
    
    def complete_with_system(self, system: str, prompt: str) -> str:
        """
        Send a prompt with a system message to Ollama.
        
        Args:
            system: The system message/instructions
            prompt: The user prompt text
            
        Returns:
            The completion text from Ollama
        """
        url = f"{self.base_url}/api/generate"
        data = {
            "model": self.model,
            "system": system,
            "prompt": prompt,
            "stream": False
        }
        
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(request) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("response", "")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Failed to connect to Ollama at {self.base_url}: {e}")
