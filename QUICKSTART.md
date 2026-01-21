# Quick Start Guide - Stream Repurpose Pipeline

## First Time Setup (One-Time Only)

### 1. Install System Dependencies

```bash
# Install FFmpeg (required for audio conversion)
brew install ffmpeg

# Install Xcode Command Line Tools (if not already installed)
xcode-select --install
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Build whisper.cpp

```bash
# Clone whisper.cpp into vendor directory
mkdir -p vendor
cd vendor
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp

# Build using CMake
cmake -B build
cmake --build build -j --config Release

# Verify the build
ls -la build/bin/whisper-cli

# Return to project root
cd ../..
```

### 4. Get a Whisper Model

You need a Whisper GGML model file. Two options:

**Option A: Use existing MacWhisper model** (if you have MacWhisper installed)
- The default config already points to: `/Users/[your-username]/Library/Application Support/MacWhisper/models/ggml-model-whisper-turbo.bin`
- Just update the username in `config.yaml`

**Option B: Download a model using whisper.cpp**
```bash
cd vendor/whisper.cpp
./models/download-ggml-model.sh base.en
# or: ./models/download-ggml-model.sh medium
cd ../..
```

Then update `config.yaml`:
```yaml
whisper:
  model_path: "vendor/whisper.cpp/models/ggml-base.en.bin"
```

### 5. Configure LLM API Key (Optional - Only for Full Pipeline)

If you want to run the full pipeline (not just transcription), set your API key:

```bash
# For OpenAI
export OPENAI_API_KEY="your-api-key-here"

# OR for Anthropic
export ANTHROPIC_API_KEY="your-api-key-here"
```

---

## Running Transcription (Every Time)

### Transcription Only (No LLM/API Key Required)

```bash
# Activate virtual environment
source venv/bin/activate

# Run transcription only
python main.py "your-video.mp4" --skip-video --skip-text
```

**What this does:**
1. Automatically converts your video to WAV format (16-bit, 16kHz, mono)
2. Transcribes using whisper.cpp on CPU (fast on Apple Silicon)
3. Saves transcript to `output/your-video/transcript.json`

**Output location:**
```
output/your-video/transcript.json
```

### Full Pipeline (Requires API Key)

```bash
# Activate virtual environment
source venv/bin/activate

# Set API key
export OPENAI_API_KEY="your-key"

# Run full pipeline
python main.py "your-video.mp4"
```

**What this does:**
1. Transcribes the video
2. Analyzes content with LLM
3. Generates video clips (long-form + shorts)
4. Creates text content (Twitter, Reddit, Medium, etc.)

---

## Common Commands Reference

```bash
# Transcription only (fastest, no API key needed)
python main.py video.mp4 --skip-video --skip-text

# Transcription + Analysis only (requires API key)
python main.py video.mp4 --skip-video --skip-text

# Skip transcription if you already have transcript.json
python main.py video.mp4 --skip-transcription

# Skip video processing (text content only)
python main.py video.mp4 --skip-video

# Skip text generation (video processing only)
python main.py video.mp4 --skip-text

# Use custom config file
python main.py video.mp4 --config custom-config.yaml
```

---

## Troubleshooting Quick Fixes

### Error: "whisper-cli not found"

```bash
cd vendor/whisper.cpp
cmake -B build
cmake --build build -j --config Release
cd ../..
```

### Error: "Metal buffer allocation error" or Segmentation Fault

This is already fixed in the code! The transcriber automatically uses CPU-only mode.

If you still see issues, verify the fix is in place:
```bash
grep "no-gpu" src/transcriber.py
# Should show: "--no-gpu",  # Disable GPU
```

### Error: "API key not found"

Only needed for full pipeline (not transcription-only):
```bash
export OPENAI_API_KEY="your-key-here"
```

### Error: "FFmpeg not found"

```bash
brew install ffmpeg
```

### Error: "Model file not found"

Update `config.yaml` with correct path:
```yaml
whisper:
  model_path: "/correct/path/to/your/model.bin"
```

---

## File Structure After First Run

```
stream-repurpose/
├── venv/                           # Python virtual environment
├── vendor/
│   └── whisper.cpp/
│       └── build/
│           └── bin/
│               └── whisper-cli     # Compiled binary
├── output/
│   └── your-video/
│       ├── transcript.json         # Transcription output
│       ├── analysis.json           # LLM analysis (if run)
│       ├── videos/                 # Video clips (if run)
│       └── *.md files              # Text content (if run)
├── config.yaml                     # Configuration
└── main.py                         # Entry point
```

---

## Tips

1. **Start with transcription only** to verify everything works before running the full pipeline
2. **The first run** may take longer as whisper.cpp initializes
3. **CPU transcription** is still very fast on Apple Silicon (M1/M2/M3 chips)
4. **Check your model path** in `config.yaml` before running
5. **Transcript files** are saved even if later steps fail

---

## Testing Your Setup

Quick test to verify everything is working:

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Test whisper-cli directly
vendor/whisper.cpp/build/bin/whisper-cli \
  -m vendor/whisper.cpp/models/for-tests-ggml-tiny.bin \
  -f vendor/whisper.cpp/samples/jfk.wav \
  --no-gpu

# 3. Test with a short video
python main.py "your-short-video.mp4" --skip-video --skip-text
```

If all three work, you're ready to go!
