#!/usr/bin/env python3
"""
Stream Repurposing Pipeline

Takes a stream recording and generates:
- Transcription with timestamps
- Long-form YouTube video (trimmed)
- Short-form clips (vertical format)
- Twitter thread, Reddit post, Medium article, Tweets, Telegram post
"""

import argparse
import os
import sys
from pathlib import Path

import yaml

from src.transcriber import Transcriber
from src.analyzer import Analyzer
from src.video_processor import VideoProcessor
from src.content_generator import ContentGenerator


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Repurpose stream recordings into multiple content formats"
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input MP4 file"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config file (default: config.yaml)"
    )
    parser.add_argument(
        "--skip-transcription",
        action="store_true",
        help="Skip transcription if transcript.json already exists"
    )
    parser.add_argument(
        "--skip-video",
        action="store_true",
        help="Skip video processing"
    )
    parser.add_argument(
        "--skip-text",
        action="store_true",
        help="Skip text content generation"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Load configuration
    config = load_config(args.config)
    
    # Create output directory
    stream_name = input_path.stem
    output_dir = Path(config["output"]["base_dir"]) / stream_name
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "videos" / "shorts").mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print(f"Stream Repurposing Pipeline")
    print("="*60)
    print(f"Input:  {input_path}")
    print(f"Output: {output_dir}")
    print("="*60 + "\n")
    
    # Step 1: Transcription
    transcript_path = output_dir / "transcript.json"
    if args.skip_transcription and transcript_path.exists():
        print("[1/4] Skipping transcription (using existing transcript.json)")
    else:
        print("[1/4] Transcribing audio...")
        whisper_cpp_path = config["whisper"].get("whisper_cpp_path", "vendor/whisper.cpp")
        transcriber = Transcriber(
            config["whisper"]["model_path"],
            whisper_cpp_path=whisper_cpp_path
        )
        transcriber.transcribe(str(input_path), str(transcript_path))
        print(f"  ✓ Transcript saved: {transcript_path.name}\n")
    
    # Step 2: LLM Analysis
    print("[2/4] Analyzing transcript...")
    analyzer = Analyzer(config["llm"])
    analysis = analyzer.analyze(str(transcript_path))
    analysis_path = output_dir / "analysis.json"
    analyzer.save_analysis(analysis, str(analysis_path))
    print(f"  ✓ Analysis saved: {analysis_path.name}\n")
    
    # Step 3: Video Processing
    if not args.skip_video:
        print("[3/4] Processing video segments...")
        processor = VideoProcessor(config.get("video", {}))
        processor.process(
            str(input_path),
            analysis,
            str(output_dir / "videos")
        )
        print(f"  ✓ Video processing complete\n")
    else:
        print("[3/4] Skipping video processing\n")
    
    # Step 4: Text Content Generation
    if not args.skip_text:
        print("[4/4] Generating text content...")
        generator = ContentGenerator(config["llm"])
        generator.generate_all(
            str(transcript_path),
            analysis,
            str(output_dir)
        )
        print(f"  ✓ Text content generation complete\n")
    else:
        print("[4/4] Skipping text content generation\n")
    
    print("="*60)
    print(f"✓ Pipeline complete! All outputs saved to:")
    print(f"  {output_dir}")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
