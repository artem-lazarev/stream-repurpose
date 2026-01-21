# Stream Repurpose - Command Cheat Sheet

## Essential Commands

### First Time Setup
```bash
# 1. Build whisper.cpp
cd vendor/whisper.cpp
cmake -B build && cmake --build build -j --config Release
cd ../..

# 2. Create Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Every Time You Use It
```bash
# Activate environment
source venv/bin/activate

# Transcription only (no API key needed)
python main.py "video.mp4" --skip-video --skip-text
```

## Command Options

| Command | Description |
|---------|-------------|
| `python main.py video.mp4` | Full pipeline (transcribe + analyze + generate) |
| `python main.py video.mp4 --skip-video --skip-text` | **Transcription only** (fastest) |
| `python main.py video.mp4 --skip-transcription` | Skip transcription (use existing) |
| `python main.py video.mp4 --skip-video` | Transcribe + generate text only |
| `python main.py video.mp4 --skip-text` | Transcribe + generate videos only |
| `python main.py video.mp4 --config custom.yaml` | Use custom config file |

## Output Locations

```
output/
└── your-video/
    ├── transcript.json          # ← Transcription output
    ├── analysis.json            # LLM analysis
    ├── videos/
    │   ├── long_form.mp4
    │   └── shorts/*.mp4
    ├── twitter_thread.md
    ├── tweets.md
    ├── reddit_post.md
    ├── medium_article.md
    └── telegram_post.md
```

## Environment Variables

```bash
# For OpenAI (GPT-4)
export OPENAI_API_KEY="sk-..."

# For Anthropic (Claude)
export ANTHROPIC_API_KEY="sk-ant-..."

# Not needed for transcription-only mode
```

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| `whisper-cli not found` | `cd vendor/whisper.cpp && cmake -B build && cmake --build build -j` |
| `API key not found` | `export OPENAI_API_KEY="your-key"` (only for full pipeline) |
| `FFmpeg not found` | `brew install ffmpeg` |
| Segmentation fault | Already fixed! Ensure you have latest code |

## Config File (`config.yaml`)

```yaml
whisper:
  model_path: "/path/to/ggml-model-whisper-turbo.bin"  # ← Update this
  whisper_cpp_path: "vendor/whisper.cpp"

llm:
  provider: "openai"  # or "anthropic" or "ollama"
  model: "gpt-4o"
  api_key_env: "OPENAI_API_KEY"

output:
  base_dir: "output"

video:
  short_form:
    min_duration: 30
    max_duration: 60
    aspect_ratio: "9:16"
```

## Testing

```bash
# Test whisper-cli directly
vendor/whisper.cpp/build/bin/whisper-cli \
  -m vendor/whisper.cpp/models/for-tests-ggml-tiny.bin \
  -f vendor/whisper.cpp/samples/jfk.wav \
  --no-gpu

# Test transcription
python main.py "test-video.mp4" --skip-video --skip-text
```

## Supported Input Formats

- ✅ MP4 (automatically converted)
- ✅ MP3 (automatically converted)
- ✅ WAV (direct processing)
- ✅ Any FFmpeg-supported format

## Performance

- **Transcription**: ~17 seconds for 1.5 minute video
- **Full Pipeline**: Depends on LLM API speed
- **CPU Usage**: Moderate on Apple Silicon (M1/M2/M3)

## Common Workflows

### Workflow 1: Quick Transcription
```bash
source venv/bin/activate
python main.py "stream.mp4" --skip-video --skip-text
# Output: output/stream/transcript.json
```

### Workflow 2: Full Content Generation
```bash
source venv/bin/activate
export OPENAI_API_KEY="your-key"
python main.py "stream.mp4"
# Output: All files in output/stream/
```

### Workflow 3: Transcription + Text Only
```bash
source venv/bin/activate
export OPENAI_API_KEY="your-key"
python main.py "stream.mp4" --skip-video
# Output: transcript.json + all .md files
```

---

📖 **Full Documentation**: See [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md)
