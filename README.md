# Video_China - Automated Video Localization Pipeline

A Python-based automation tool that converts Chinese videos (from Douyin/Bilibili) to Vietnamese with automatic dubbing. The pipeline handles video downloading, speech recognition, translation, and voice synthesis.

## 🎯 Features

- ✅ **Video Download**: Supports Douyin, Bilibili, and other platforms via yt-dlp
- ✅ **Speech Recognition**: Converts Chinese audio to text using OpenAI Whisper
- ✅ **AI Translation**: Translates Chinese subtitles to Vietnamese using GPT-4o
- ✅ **Voice Synthesis**: Generates Vietnamese speech using Azure Cognitive Services
- ✅ **Audio Alignment**: Automatically adjusts TTS speed to match original timing
- ✅ **Video Composition**: Blends new audio with video and applies anti-copyright filters
- ✅ **GUI Interface**: Modern CustomTkinter-based UI for easy control
- ✅ **CLI Interface**: Direct Python execution for automation

## 📋 Requirements

### System Dependencies
- **FFmpeg**: Required for audio/video processing
  - Windows: `choco install ffmpeg` or download from https://ffmpeg.org/
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

### Python Version
- Python 3.8+

### API Keys Required
1. **OpenAI API Key**: For Whisper (transcription) and GPT-4o (translation)
   - Get it at: https://platform.openai.com/api-keys
2. **Azure Speech Key**: For Vietnamese text-to-speech
   - Get it at: https://portal.azure.com/

## 🚀 Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/hater0355/Video_China.git
cd Video_China
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure API Keys

Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx
AZURE_SPEECH_KEY=xxxxxxxxxxxxxxxxxxxx
AZURE_SPEECH_REGION=eastus
```

Lấy keys từ:
- **OpenAI**: https://platform.openai.com/api-keys
- **Azure Speech**: https://portal.azure.com/

## 🎮 Usage

### Option 1: GUI Interface (Recommended)
```bash
python run_gui.py
```

Then:
1. Enter a Douyin/Bilibili video URL
2. Select output directory (or use default)
3. Enter API keys (or use .env values)
4. Click "START PIPELINE"
5. Monitor progress in the log console

### Option 2: Command Line
```bash
python main.py
```

Then enter the video URL when prompted:
```
Enter Douyin/Bilibili video URL: https://www.bilibili.com/video/BVxxxxxxxxxxxx
```

## 📁 Directory Structure

```
Video_China/
├── main.py                 # CLI entry point
├── run_gui.py             # GUI entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .env                  # Your API keys (create this)
│
├── video_downloader.py   # Video downloading module
├── audio_processor.py    # Audio extraction & transcription
├── translator.py         # Chinese→Vietnamese translation
├── voice_generator.py    # TTS and audio alignment
├── video_composer.py     # Final video assembly
├── gui.py               # GUI interface
│
└── output/              # Generated videos (auto-created)
```

## 📊 Pipeline Steps

1. **Download**: Fetches video from URL
2. **Extract**: Extracts audio from video (16kHz mono WAV)
3. **Transcribe**: Converts Chinese audio to text with timestamps
4. **Translate**: Translates to Vietnamese using AI
5. **Synthesize**: Generates Vietnamese voice (TTS)
6. **Align**: Adjusts voice speed to match original timing
7. **Compose**: Merges video + new audio with original audio at 10% volume
8. **Output**: Saves final video to `output/` folder

## 🔧 Troubleshooting

### FFmpeg Not Found
```bash
# Windows (if Chocolatey installed):
choco install ffmpeg

# macOS:
brew install ffmpeg

# Linux:
sudo apt install ffmpeg
```

### API Key Errors
- Verify keys are correct in `.env` file
- Check API quotas and billing on OpenAI/Azure portals
- Ensure keys have proper permissions

### Empty Transcription
- Check audio volume in original video
- Verify Whisper API quota on OpenAI

### Memory Issues
- Close other applications
- Reduce video resolution if possible

### FFmpeg Filter Errors
- Ensure FFmpeg version is recent (`ffmpeg -version`)
- Check log for specific filter syntax issues

## 💡 Tips

- **Cost Optimization**: Use shorter videos for testing
- **Batch Processing**: Create a script to loop over multiple URLs
- **Quality**: Use `https://...` URLs (more stable than mobile links)
- **Debugging**: Check `workspace/` folder for intermediate files before cleanup

## 🤝 Contributing

Issues and pull requests are welcome!

## 📝 License

MIT License

## ⚠️ Disclaimer

This tool is for educational and personal use only. Respect copyright laws and platform terms of service when downloading videos.

---

**Questions?** Check the logs for detailed error messages or open an issue on GitHub.
