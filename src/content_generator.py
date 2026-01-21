"""Text content generation module."""

import json
from pathlib import Path

from .llm import get_llm_provider


class ContentGenerator:
    """Generate text content from transcript and analysis."""
    
    CONTENT_TYPES = [
        ("twitter_thread", "twitter_thread.txt", "twitter_thread.md"),
        ("reddit_post", "reddit_post.txt", "reddit_post.md"),
        ("medium_article", "medium_article.txt", "medium_article.md"),
        ("tweets", "tweets.txt", "tweets.md"),
        ("telegram_post", "telegram_post.txt", "telegram_post.md"),
    ]
    
    def __init__(self, llm_config: dict):
        """
        Initialize the content generator.
        
        Args:
            llm_config: LLM configuration from config.yaml
        """
        self.llm = get_llm_provider(llm_config)
        self.prompts_dir = Path("prompts")
    
    def generate_all(
        self,
        transcript_path: str,
        analysis: dict,
        output_dir: str
    ):
        """
        Generate all text content types.
        
        Args:
            transcript_path: Path to transcript JSON
            analysis: Analysis dictionary from LLM
            output_dir: Directory to save generated content
        """
        # Load transcript
        with open(transcript_path, "r") as f:
            transcript = json.load(f)
        
        output_path = Path(output_dir)
        
        for content_type, prompt_file, output_file in self.CONTENT_TYPES:
            print(f"  Generating {content_type}...")
            content = self.generate(
                content_type,
                transcript,
                analysis,
                prompt_file
            )
            
            # Save content
            output_file_path = output_path / output_file
            with open(output_file_path, "w") as f:
                f.write(content)
    
    def generate(
        self,
        content_type: str,
        transcript: dict,
        analysis: dict,
        prompt_file: str
    ) -> str:
        """
        Generate a specific type of content.
        
        Args:
            content_type: Type of content to generate
            transcript: Transcript dictionary
            analysis: Analysis dictionary
            prompt_file: Name of the prompt template file
            
        Returns:
            Generated content as string
        """
        # Load prompt template
        prompt_path = self.prompts_dir / prompt_file
        with open(prompt_path, "r") as f:
            prompt_template = f.read()
        
        # Format transcript
        transcript_text = self._format_transcript(transcript)
        
        # Format analysis highlights
        highlights = self._format_highlights(analysis)
        
        # Fill prompt template
        prompt = prompt_template.replace("{transcript}", transcript_text)
        prompt = prompt.replace("{highlights}", highlights)
        prompt = prompt.replace("{title}", analysis.get("title", ""))
        
        # Generate content
        response = self.llm.complete(prompt)
        
        return response.strip()
    
    def _format_transcript(self, transcript: dict) -> str:
        """Format transcript for LLM consumption."""
        lines = []
        for segment in transcript["segments"]:
            lines.append(segment["text"])
        return "\n".join(lines)
    
    def _format_highlights(self, analysis: dict) -> str:
        """Format analysis highlights for prompts."""
        highlights = analysis.get("highlights", [])
        if isinstance(highlights, list):
            return "\n".join(f"- {h}" for h in highlights)
        return str(highlights)
