# Technical Fixes and Changes

## Issue: Transcription Failing with Segmentation Fault

**Date**: 2026-01-22

### Problem

The transcription pipeline was failing with a segmentation fault (exit code 139) when trying to transcribe video files. The error was:

```
ggml_metal_buffer_init: error: failed to allocate buffer, size = 2.20 MiB
subprocess.CalledProcessError: Command [...] died with <Signals.SIGSEGV: 11>
```

### Root Causes

1. **Metal GPU Buffer Allocation Issue**: The Metal backend in whisper.cpp was failing to allocate GPU memory on some systems, causing crashes
2. **Video Format Incompatibility**: whisper-cli only supports 16-bit WAV files (16kHz, mono, PCM), but the pipeline was trying to pass MP4 files directly
3. **Build System Mismatch**: README suggested using `make` but the correct build method is CMake

### Solutions Implemented

#### 1. Disabled Metal GPU Acceleration (`src/transcriber.py`)

Added `--no-gpu` flag to whisper-cli command:

```python
cmd = [
    str(self.whisper_cli),
    "-m", str(self.model_path),
    "-f", str(audio_file),
    "-oj",  # Output JSON
    "-of", str(tmp_base),
    "-np",  # No prints
    "-l", "en",
    "--no-gpu",  # Disable GPU to avoid Metal buffer allocation errors
]
```

**Impact**: Transcription now runs on CPU using Accelerate framework, which is still very fast on Apple Silicon while being more stable.

#### 2. Automatic Audio Format Conversion (`src/transcriber.py`)

Added logic to automatically convert any input format to 16-bit WAV:

```python
# Check if conversion is needed
needs_conversion = input_file.suffix.lower() != '.wav'

if needs_conversion:
    print(f"Converting {input_file.suffix} to WAV format...")
    wav_file = Path(tmp_dir) / "input.wav"
    convert_cmd = [
        "ffmpeg", "-i", str(input_file),
        "-ar", "16000",  # 16kHz sample rate
        "-ac", "1",      # Mono
        "-c:a", "pcm_s16le",  # 16-bit PCM
        "-y",
        str(wav_file)
    ]
    subprocess.run(convert_cmd, check=True, capture_output=True)
    audio_file = wav_file
else:
    audio_file = input_file
```

**Impact**: Users can now pass MP4, MP3, or any FFmpeg-supported format directly without manual conversion.

#### 3. Documentation Updates

**Updated Files**:
- `README.md`: 
  - Fixed build instructions to use CMake instead of make
  - Added comprehensive troubleshooting section for Metal GPU issues
  - Added "Transcription Only" quick start
  - Documented automatic format conversion
  
- `QUICKSTART.md` (new):
  - Step-by-step setup guide
  - Common commands reference
  - Troubleshooting quick fixes
  - Testing instructions

- `FIXES.md` (this file):
  - Technical documentation of changes
  - Root cause analysis
  - Implementation details

### Testing Performed

1. **Test 1**: Verified whisper-cli works with `--no-gpu` flag
   ```bash
   vendor/whisper.cpp/build/bin/whisper-cli \
     -m vendor/whisper.cpp/models/for-tests-ggml-tiny.bin \
     -f vendor/whisper.cpp/samples/jfk.wav \
     --no-gpu
   ```
   ✅ **Result**: Success (processed in ~380ms)

2. **Test 2**: End-to-end transcription of MP4 file
   ```bash
   python main.py "2026-01-04 07-10-42.mp4" --skip-video --skip-text
   ```
   ✅ **Result**: Success
   - Automatic conversion from MP4 to WAV
   - Transcription completed
   - Output saved to `output/2026-01-04 07-10-42/transcript.json`

3. **Test 3**: Verified transcript quality
   - ✅ Timestamps are accurate
   - ✅ Text transcription is correct
   - ✅ JSON format is valid

### Files Modified

```
src/transcriber.py          # Added --no-gpu flag and auto-conversion
README.md                   # Updated build instructions and troubleshooting
QUICKSTART.md               # New file - setup guide
FIXES.md                    # New file - this documentation
```

### Performance Impact

**Before** (with Metal GPU attempt):
- ❌ Crashed with segmentation fault

**After** (CPU-only with Accelerate):
- ✅ Stable and reliable
- ~1.5 minute video transcribed in ~17 seconds (including conversion)
- CPU usage is acceptable on Apple Silicon
- No GPU memory issues

### Recommendations

1. ✅ **Done**: Always use CMake to build whisper.cpp
2. ✅ **Done**: Use CPU-only mode for stability
3. ⚠️ **Future**: Consider adding Metal GPU support as an optional flag once upstream issues are resolved
4. ⚠️ **Future**: Add option to keep converted WAV files for debugging
5. ⚠️ **Future**: Add progress bar for long transcriptions

### Related Issues

- whisper.cpp Metal backend buffer allocation issues (common on some macOS configurations)
- whisper-cli audio format requirements (16-bit WAV only)

### Verification Commands

To verify the fixes are in place:

```bash
# Check for --no-gpu flag
grep -n "no-gpu" src/transcriber.py

# Check for conversion logic
grep -n "needs_conversion" src/transcriber.py

# Check for FFmpeg conversion command
grep -n "ffmpeg" src/transcriber.py
```

### Rollback Instructions

If these changes need to be reverted:

1. Remove `--no-gpu` flag from `src/transcriber.py` line ~70
2. Remove format conversion logic (lines ~54-72)
3. Revert README.md to previous version

However, **rollback is not recommended** as it would re-introduce the crashes.
