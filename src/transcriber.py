"""Whisper transcription module with timestamps using whisper.cpp CLI."""

import json
import os
import subprocess
import tempfile
from pathlib import Path


class Transcriber:
    """Transcribe audio using local Whisper GGML model via whisper.cpp CLI."""
    
    def __init__(self, model_path: str, whisper_cpp_path: str = "vendor/whisper.cpp"):
        """
        Initialize the transcriber.
        
        Args:
            model_path: Path to the Whisper GGML model file
            whisper_cpp_path: Path to the whisper.cpp repository root
        """
        self.model_path = Path(model_path).expanduser().resolve()
        self.whisper_cpp_path = Path(whisper_cpp_path).expanduser().resolve()
        self.whisper_cli = self.whisper_cpp_path / "build" / "bin" / "whisper-cli"
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        if not self.whisper_cli.exists():
            raise FileNotFoundError(
                f"whisper-cli not found at {self.whisper_cli}. "
                f"Please build whisper.cpp first: cd {self.whisper_cpp_path} && make -j"
            )
    
    def transcribe(self, input_path: str, output_path: str) -> dict:
        """
        Transcribe an audio/video file and save timestamped transcript.
        
        Args:
            input_path: Path to the input media file
            output_path: Path to save the transcript JSON
            
        Returns:
            Dictionary containing segments with timestamps
        """
        input_file = Path(input_path).expanduser().resolve()
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Create output directory if needed
        output_file = Path(output_path).expanduser().resolve()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # whisper-cli only supports 16-bit WAV files
        # Convert input to required format if needed
        needs_conversion = input_file.suffix.lower() != '.wav'
        
        # Create temporary directory for whisper.cpp JSON output
        # whisper-cli adds .json extension automatically
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_base = Path(tmp_dir) / "whisper_output"
            
            # Convert to 16-bit WAV if needed
            if needs_conversion:
                print(f"  → Converting {input_file.suffix} to audio format...")
                wav_file = Path(tmp_dir) / "input.wav"
                # Convert to 16-bit PCM, 16kHz, mono WAV (required by whisper-cli)
                convert_cmd = [
                    "ffmpeg", "-i", str(input_file),
                    "-ar", "16000",  # 16kHz sample rate
                    "-ac", "1",  # Mono
                    "-c:a", "pcm_s16le",  # 16-bit PCM
                    "-y",  # Overwrite output file
                    str(wav_file)
                ]
                subprocess.run(convert_cmd, check=True, capture_output=True)
                print(f"  → Audio conversion complete")
                audio_file = wav_file
            else:
                audio_file = input_file
            
            # Build whisper-cli command
            # -oj: output JSON format
            # -m: model path
            # -f: input file
            # -of: output file (without extension, whisper-cli adds .json)
            # -np: no prints (cleaner output)
            # --no-gpu: disable GPU (Metal has buffer allocation issues)
            cmd = [
                str(self.whisper_cli),
                "-m", str(self.model_path),
                "-f", str(audio_file),
                "-oj",  # Output JSON
                "-of", str(tmp_base),  # Output file without extension
                "-np",  # No prints
                "-l", "en",  # Language (can be made configurable)
                "--no-gpu",  # Disable GPU to avoid Metal buffer allocation errors
            ]
            
            # Run whisper-cli
            print(f"  → Running transcription (this may take a few minutes)...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.whisper_cpp_path)
            )
            print(f"  → Transcription complete")
            
            # Read the JSON output (whisper-cli adds .json extension)
            whisper_output_path = Path(str(tmp_base) + ".json")
            
            if not whisper_output_path.exists():
                raise RuntimeError(
                    f"whisper-cli did not generate output file. "
                    f"Expected: {whisper_output_path}\n"
                    f"stderr: {result.stderr}\n"
                    f"stdout: {result.stdout}"
                )
            
            # Parse whisper.cpp JSON format and convert to our format
            with open(whisper_output_path, 'r') as f:
                whisper_data = json.load(f)
            
            # Convert whisper.cpp format to our format
            # whisper.cpp format: {"transcription": [{"timestamps": {...}, "offsets": {"from": ms, "to": ms}, "text": "..."}, ...]}
            # Our format: {"segments": [{"start": seconds, "end": seconds, "text": "..."}, ...]}
            transcript = {
                "segments": []
            }
            
            if "transcription" in whisper_data:
                for segment in whisper_data["transcription"]:
                    # Get offsets in milliseconds, convert to seconds
                    offsets = segment.get("offsets", {})
                    start_ms = offsets.get("from", 0)
                    end_ms = offsets.get("to", 0)
                    
                    transcript["segments"].append({
                        "start": start_ms / 1000.0,  # Convert milliseconds to seconds
                        "end": end_ms / 1000.0,
                        "text": segment.get("text", "").strip()
                    })
            
            # Save to our output format
            with open(output_file, 'w') as f:
                json.dump(transcript, f, indent=2)
            
            return transcript
    
    def cleanup(self):
        """No-op for compatibility - whisper-cli doesn't need cleanup."""
        pass
