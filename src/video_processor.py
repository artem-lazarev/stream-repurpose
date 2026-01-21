"""FFmpeg video processing module."""

import subprocess
from pathlib import Path
from typing import Optional


class VideoProcessor:
    """Process video segments using FFmpeg."""
    
    def __init__(self, video_config: dict):
        """
        Initialize the video processor.
        
        Args:
            video_config: Video configuration from config.yaml
        """
        self.config = video_config
        self.short_form_config = video_config.get("short_form", {
            "min_duration": 30,
            "max_duration": 60,
            "aspect_ratio": "9:16"
        })
    
    def process(self, input_path: str, analysis: dict, output_dir: str):
        """
        Process video based on analysis results.
        
        Args:
            input_path: Path to the input video file
            analysis: Analysis dictionary from LLM
            output_dir: Directory to save processed videos
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Process long-form video
        if "long_form" in analysis:
            print(f"  → Creating long-form video...")
            long_form_output = output_path / "long_form.mp4"
            self._process_long_form(
                input_path,
                analysis["long_form"],
                str(long_form_output)
            )
            print(f"  → Long-form video saved")
        
        # Process short-form clips
        if "short_form" in analysis:
            shorts_dir = output_path / "shorts"
            shorts_dir.mkdir(parents=True, exist_ok=True)
            total_clips = len(analysis["short_form"])
            print(f"  → Creating {total_clips} short-form clips...")
            for i, clip in enumerate(analysis["short_form"], 1):
                clip_output = shorts_dir / f"short_{i:02d}.mp4"
                self._process_short_form(
                    input_path,
                    clip,
                    str(clip_output)
                )
                print(f"    • Clip {i}/{total_clips} complete")
            print(f"  → All short-form clips saved")
    
    def _process_long_form(self, input_path: str, segments: list, output_path: str):
        """
        Create long-form video from segments.
        
        Args:
            input_path: Path to input video
            segments: List of segment dictionaries with start/end times
            output_path: Path to save output video
        """
        if not segments:
            return
        
        # If single continuous segment, simple cut
        if len(segments) == 1:
            self._cut_segment(
                input_path,
                segments[0]["start"],
                segments[0]["end"],
                output_path
            )
        else:
            # Multiple segments - need to concatenate
            self._concatenate_segments(input_path, segments, output_path)
    
    def _process_short_form(self, input_path: str, clip: dict, output_path: str):
        """
        Create short-form vertical video clip.
        
        Args:
            input_path: Path to input video
            clip: Clip dictionary with start/end times
            output_path: Path to save output video
        """
        start = clip["start"]
        end = clip["end"]
        duration = end - start
        
        # Build FFmpeg command with vertical crop
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ss", str(start),
            "-t", str(duration),
            "-vf", "crop=ih*9/16:ih,scale=1080:1920",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-preset", "fast",
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    def _cut_segment(
        self,
        input_path: str,
        start: float,
        end: float,
        output_path: str,
        vertical: bool = False
    ):
        """Cut a single segment from video."""
        duration = end - start
        
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", input_path,
            "-t", str(duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-preset", "fast",
        ]
        
        if vertical:
            cmd.extend(["-vf", "crop=ih*9/16:ih,scale=1080:1920"])
        
        cmd.append(output_path)
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    def _concatenate_segments(
        self,
        input_path: str,
        segments: list,
        output_path: str
    ):
        """Concatenate multiple segments into one video."""
        import tempfile
        import os
        
        # Create temporary directory for segment files
        with tempfile.TemporaryDirectory() as temp_dir:
            segment_files = []
            
            # Cut each segment
            for i, segment in enumerate(segments):
                segment_path = os.path.join(temp_dir, f"segment_{i:03d}.mp4")
                self._cut_segment(
                    input_path,
                    segment["start"],
                    segment["end"],
                    segment_path
                )
                segment_files.append(segment_path)
            
            # Create concat file
            concat_file = os.path.join(temp_dir, "concat.txt")
            with open(concat_file, "w") as f:
                for segment_path in segment_files:
                    f.write(f"file '{segment_path}'\n")
            
            # Concatenate segments
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
