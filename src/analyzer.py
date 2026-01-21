"""LLM analysis module for identifying content segments."""

import json
from pathlib import Path

from .llm import get_llm_provider


class Analyzer:
    """Analyze transcript using LLM to identify content segments."""
    
    def __init__(self, llm_config: dict):
        """
        Initialize the analyzer.
        
        Args:
            llm_config: LLM configuration from config.yaml
        """
        self.llm = get_llm_provider(llm_config)
        self.prompt_path = Path("prompts/analysis.txt")
    
    def _load_prompt(self) -> str:
        """Load the analysis prompt template."""
        with open(self.prompt_path, "r") as f:
            return f.read()
    
    def analyze(self, transcript_path: str) -> dict:
        """
        Analyze transcript to identify content segments.
        
        Args:
            transcript_path: Path to the transcript JSON file
            
        Returns:
            Analysis dictionary with segment information
        """
        # Load transcript
        with open(transcript_path, "r") as f:
            transcript = json.load(f)
        
        # Format transcript for LLM
        transcript_text = self._format_transcript(transcript)
        
        # Load and fill prompt
        prompt_template = self._load_prompt()
        prompt = prompt_template.replace("{transcript}", transcript_text)
        
        # Get LLM response
        response = self.llm.complete(prompt)
        
        # Parse JSON from response
        analysis = self._parse_response(response)
        
        return analysis
    
    def _format_transcript(self, transcript: dict) -> str:
        """Format transcript for LLM consumption."""
        lines = []
        for segment in transcript["segments"]:
            start = self._format_time(segment["start"])
            end = self._format_time(segment["end"])
            lines.append(f"[{start} - {end}] {segment['text']}")
        return "\n".join(lines)
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _parse_response(self, response: str) -> dict:
        """Parse JSON from LLM response."""
        # Try to find JSON in the response
        try:
            # Look for JSON block in markdown code fence
            if "```json" in response:
                start = response.index("```json") + 7
                end = response.index("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.index("```") + 3
                end = response.index("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
    
    def save_analysis(self, analysis: dict, output_path: str):
        """Save analysis to a JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(analysis, f, indent=2)
