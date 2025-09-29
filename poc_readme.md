# StreamScribe Proof of Concept

A simple Python script demonstrating real-time audio transcription from YouTube videos using OpenAI's Whisper model.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the POC

#### Basic Usage
```bash
python streamscribe_poc.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

#### With Different Model Size
```bash
python streamscribe_poc.py "https://www.youtube.com/watch?v=VIDEO_ID" --model small
```

#### Run Test
```bash
python test_poc.py
```

## 📋 Features Demonstrated

- ✅ YouTube video information extraction
- ✅ Audio stream URL extraction  
- ✅ Whisper model integration
- ✅ Basic audio transcription
- ✅ Timestamped output
- ✅ Error handling

## 🎛️ Model Options

Choose from different Whisper model sizes based on your needs:

- `tiny` - Fastest, least accurate (~1GB VRAM)
- `base` - Good balance (default) (~1GB VRAM) 
- `small` - Better accuracy (~2GB VRAM)
- `medium` - High accuracy (~5GB VRAM)
- `large` - Best accuracy (~10GB VRAM)

## 📝 Example Output

```
🚀 Starting StreamScribe POC...
📺 Target URL: https://www.youtube.com/watch?v=jNQXAC9IVRw
Loading Whisper model (tiny)...
✅ Whisper model loaded successfully
📋 Extracting video information...
📹 Video: Me at the zoo
👤 Uploader: jawed
⏱️  Duration: 19 seconds
🎵 Starting audio stream simulation...
📥 Downloading audio stream...
✅ Audio download complete
🎤 Starting transcription processor...
🔄 Processing audio chunk...
🔊 Running Whisper transcription...
🌍 Detected language: en

[14:37:18] 📝 Transcript:
'Alright so here we are one of the elephants. The cool thing for these guys is that they have really really long prompts and that's cool. And that's pretty much all it is to say.'

✅ StreamScribe POC completed!
```

## ⚠️ Limitations

This is a **proof of concept** with the following limitations:

1. **Not True Streaming**: Downloads entire audio file instead of streaming chunks
2. **Single Chunk Processing**: Processes entire audio at once, not in real-time segments
3. **No WebSocket Interface**: Output is console-only
4. **Basic Error Handling**: Minimal error recovery
5. **No Rate Limiting**: Doesn't implement YouTube API rate limiting

## 🔧 Next Steps for Full Implementation

1. Implement true audio streaming with chunk buffering
2. Add WebSocket server for real-time transcript delivery
3. Implement proper error handling and reconnection logic
4. Add support for multiple ASR providers
5. Create web interface for user interaction
6. Add rate limiting and respectful API usage
7. Implement audio preprocessing and normalization

## 🛠️ Requirements

- Python 3.8+
- FFmpeg (for audio processing)
- Internet connection (for YouTube access and model downloads)
- ~1-10GB disk space (depending on Whisper model size)

## 📖 Code Structure

- `streamscribe_poc.py` - Main POC implementation
- `test_poc.py` - Simple test script
- `requirements.txt` - Python dependencies
- `poc_readme.md` - This documentation