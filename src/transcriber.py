"""Whisper transcription module with timestamps."""

import json
from pathlib import Path


class Transcriber:
    """Transcribe audio using local Whisper GGML model via pywhispercpp."""
    
    def __init__(self, model_path: str):
        """
        Initialize the transcriber.
        
        Args:
            model_path: Path to the Whisper GGML model file
        """
        self.model_path = model_path
        self._model = None
    
    def _load_model(self):
        """Lazy load the Whisper model from a local GGML file."""
        if self._model is None:
            from pywhispercpp.model import Model
            import os
            
            # Disable Metal/GPU to avoid buffer allocation issues - use CPU only
            # This environment variable may help, but the error might be non-fatal
            os.environ.setdefault("GGML_METAL_DISABLE", "1")
            
            # Model class accepts file paths directly - it checks Path(model).is_file()
            # If the path exists, it loads from file; otherwise treats it as a model name
            # n_threads is passed as a keyword argument (part of **params)
            self._model = Model(self.model_path, n_threads=4)
        return self._model
    
    def transcribe(self, input_path: str, output_path: str) -> dict:
        """
        Transcribe an audio/video file and save timestamped transcript.
        
        Args:
            input_path: Path to the input media file
            output_path: Path to save the transcript JSON
            
        Returns:
            Dictionary containing segments with timestamps
        """
        model = self._load_model()
        
        # Transcribe the file
        segments = model.transcribe(input_path)
        
        # Format output with timestamps
        transcript = {
            "segments": [
                {
                    "start": segment.t0 / 100.0,  # Convert to seconds
                    "end": segment.t1 / 100.0,
                    "text": segment.text.strip()
                }
                for segment in segments
            ]
        }
        
        # Save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(transcript, f, indent=2)
        
        return transcript
