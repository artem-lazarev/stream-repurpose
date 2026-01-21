# Stream Repurposing Pipeline

A powerful Python pipeline that automatically transcribes stream recordings, analyzes content with AI, and generates multiple content formats for various platforms. Transform a single stream recording into YouTube videos, Twitter threads, Reddit posts, Medium articles, and more.

## 🎯 Overview

This tool takes a stream recording (MP4 video file) and automatically:

1. **Transcribes** the audio using a local Whisper model (no API costs)
2. **Analyzes** the content with an LLM to identify key segments and highlights
3. **Generates** long-form and short-form video clips
4. **Creates** platform-specific text content (Twitter, Reddit, Medium, Telegram, etc.)

All outputs are saved as files for manual review before publishing.

## ✨ Features

- **Local Transcription**: Uses Whisper GGML models (no API costs, works offline)
- **Multi-LLM Support**: Works with OpenAI, Anthropic Claude, or local Ollama
- **Intelligent Content Analysis**: AI identifies valuable segments, viral moments, and key highlights
- **Video Processing**: Automatically creates:
  - Long-form YouTube videos (trimmed to main content)
  - Short-form vertical clips (9:16 aspect ratio for TikTok/Shorts/Reels)
- **Multi-Platform Text Generation**:
  - Twitter threads
  - Individual tweets
  - Reddit posts
  - Medium articles
  - Telegram posts
- **Configurable**: Easy YAML-based configuration
- **Modular Architecture**: Clean, extensible codebase

## 🏗️ Architecture

```
Input MP4 → Whisper Transcription → LLM Analysis → Video Processing + Text Generation
                                              ↓
                    Long-form Video | Short Clips | Twitter | Reddit | Medium | etc.
```

## 📋 Requirements

- Python 3.9+
- FFmpeg (for video processing)
- A Whisper GGML model file (or use built-in models)
- An LLM API key (OpenAI, Anthropic, or local Ollama)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd stream-repurpose
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `choco install ffmpeg`

### 5. Get a Whisper Model

You have two options:

**Option A: Use a local GGML model file**
- Download a Whisper GGML model (e.g., from [MacWhisper](https://goodsnooze.gumroad.com/l/macwhisper) or [whisper.cpp releases](https://github.com/ggerganov/whisper.cpp/releases))
- Update the `model_path` in `config.yaml`

**Option B: Use built-in models**
- The pipeline will automatically download models like `tiny`, `base`, `small`, `medium`, `large-v3-turbo`
- Just use the model name in your config

## ⚙️ Configuration

Edit `config.yaml` to configure the pipeline:

```yaml
whisper:
  model_path: "/path/to/your/ggml-model-whisper-turbo.bin"
  # OR use a model name: "large-v3-turbo"

llm:
  provider: "openai"  # Options: "openai", "anthropic", "ollama"
  model: "gpt-4o"
  api_key_env: "OPENAI_API_KEY"  # Environment variable name

output:
  base_dir: "output"

video:
  short_form:
    min_duration: 30  # seconds
    max_duration: 60  # seconds
    aspect_ratio: "9:16"
```

### Setting up API Keys

**For OpenAI:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**For Anthropic:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**For Ollama (local):**
- Install Ollama from [ollama.ai](https://ollama.ai)
- Run `ollama pull llama3` (or your preferred model)
- No API key needed

⚠️ **CRITICAL SECURITY WARNING**: 
- **NEVER commit API keys to your repository**
- Always use environment variables (as shown above)
- The `config.yaml` file should reference environment variable names, not actual keys
- If you accidentally commit a key, rotate it immediately in your provider's dashboard
- Consider using a `.env` file with `python-dotenv` for local development (and add `.env` to `.gitignore`)

## 📖 Usage

### Basic Usage

```bash
python main.py stream-1-raw.mp4
```

This will:
1. Transcribe the video
2. Analyze the transcript with the LLM
3. Generate video clips
4. Create all text content formats

### Advanced Options

```bash
# Skip video processing (faster for testing)
python main.py stream-1-raw.mp4 --skip-video

# Skip text generation
python main.py stream-1-raw.mp4 --skip-text

# Skip transcription (use existing transcript.json)
python main.py stream-1-raw.mp4 --skip-transcription

# Use a custom config file
python main.py stream-1-raw.mp4 --config custom-config.yaml
```

### Output Structure

After processing, you'll find all outputs in `output/{stream_name}/`:

```
output/
└── stream-1-raw/
    ├── transcript.json          # Timestamped transcript
    ├── analysis.json            # LLM analysis with segments
    ├── videos/
    │   ├── long_form.mp4        # Main content video
    │   └── shorts/
    │       ├── short_01.mp4     # Vertical clips
    │       ├── short_02.mp4
    │       └── ...
    ├── twitter_thread.md        # Twitter thread
    ├── tweets.md                # Individual tweets
    ├── reddit_post.md           # Reddit post
    ├── medium_article.md        # Medium article
    └── telegram_post.md        # Telegram post
```

## 🎨 Customizing Prompts

All prompts are stored in the `prompts/` directory and can be customized:

- `analysis.txt` - Prompt for analyzing the transcript
- `twitter_thread.txt` - Twitter thread generation
- `tweets.txt` - Individual tweets
- `reddit_post.txt` - Reddit post format
- `medium_article.txt` - Medium article format
- `telegram_post.txt` - Telegram post format

Edit these files to change the tone, style, or format of generated content.

## 🔧 Project Structure

```
stream-repurpose/
├── main.py                  # Entry point
├── config.yaml              # Configuration file
├── requirements.txt         # Python dependencies
├── src/
│   ├── transcriber.py       # Whisper transcription
│   ├── analyzer.py          # LLM analysis
│   ├── video_processor.py   # FFmpeg video processing
│   ├── content_generator.py # Text content generation
│   └── llm/
│       ├── base.py          # Abstract LLM interface
│       ├── openai_provider.py
│       ├── anthropic_provider.py
│       └── ollama_provider.py
├── prompts/                 # Prompt templates
└── output/                  # Generated content
```

## 🐛 Troubleshooting

### Transcription Issues

**Problem**: Model fails to load
- **Solution**: Check that the model path in `config.yaml` is correct
- **Alternative**: Use a built-in model name like `"large-v3-turbo"`

**Problem**: Metal/GPU allocation errors on macOS
- **Solution**: The pipeline will fall back to CPU automatically. This is normal.

### LLM API Issues

**Problem**: API key not found
- **Solution**: Make sure you've set the environment variable:
  ```bash
  export OPENAI_API_KEY="your-key"
  ```

**Problem**: Rate limits or API errors
- **Solution**: The pipeline will show the error. Check your API key and account limits.

### Video Processing Issues

**Problem**: FFmpeg not found
- **Solution**: Install FFmpeg (see Installation section)

**Problem**: Video processing fails
- **Solution**: Check that the input video file is valid and not corrupted

## 📝 Example Workflow

1. **Record your stream** → Save as `my-stream.mp4`

2. **Configure the pipeline**:
   ```bash
   # Set your API key
   export OPENAI_API_KEY="sk-..."
   
   # Edit config.yaml if needed
   ```

3. **Run the pipeline**:
   ```bash
   python main.py my-stream.mp4
   ```

4. **Review outputs** in `output/my-stream/`

5. **Edit and publish** the generated content

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🔒 Security Best Practices

1. **Never commit API keys** - Always use environment variables
2. **Use `.gitignore`** - The repository includes a `.gitignore` file to prevent committing sensitive data
3. **Rotate keys if exposed** - If you accidentally commit a key, rotate it immediately
4. **Use separate keys for development** - Don't use production API keys for testing

## 📄 License

[Add your license here - MIT, Apache 2.0, etc.]

## 🙏 Acknowledgments

- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) for the Whisper implementation
- [pywhispercpp](https://github.com/absadiki/pywhispercpp) for Python bindings
- OpenAI for Whisper and GPT models
- Anthropic for Claude models

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Made with ❤️ for content creators**
