# StreamScribe Enhanced - Usage Guide

## 🚀 Enhanced Features

### ✨ New Capabilities
- **Chunked Processing**: Handles hours-long videos efficiently
- **Real-time Progress**: Live progress bar with time estimates  
- **Graceful Interruption**: Ctrl+C saves progress, resume anytime
- **Multiple Formats**: Outputs TXT, JSON, and SRT subtitle files
- **Memory Efficient**: Processes in small chunks, low memory usage
- **Overlap Processing**: Chunks overlap for better transcription accuracy

## 📋 Quick Start

### 1. Basic Usage
```bash
python streamscribe_enhanced.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 2. With Custom Settings
```bash
python streamscribe_enhanced.py "URL" --model base --chunk-duration 30 --overlap 5
```

### 3. Interactive Testing
```bash
python test_enhanced.py
```

## ⚙️ Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `--model` | `base` | Whisper model: tiny/base/small/medium/large |
| `--chunk-duration` | `30` | Audio chunk size in seconds |
| `--overlap` | `5` | Overlap between chunks in seconds |
| `--output-dir` | `transcripts` | Output directory |

## 📊 Model Comparison for Long Videos

| Model | Speed | Accuracy | Memory | Best For |
|-------|-------|----------|---------|----------|
| `tiny` | ⚡⚡⚡⚡ | ⭐⭐ | ~1GB | Quick testing |
| `base` | ⚡⚡⚡ | ⭐⭐⭐ | ~1GB | **Recommended** |  
| `small` | ⚡⚡ | ⭐⭐⭐⭐ | ~2GB | High accuracy |
| `medium` | ⚡ | ⭐⭐⭐⭐⭐ | ~5GB | Production quality |

## 🎯 For Long Videos (3+ hours)

### Recommended Settings:
```bash
python streamscribe_enhanced.py "LONG_VIDEO_URL" \
    --model base \
    --chunk-duration 30 \
    --overlap 5 \
    --output-dir "long_transcripts"
```

### Expected Performance:
- **3-hour video**: ~2-4 hours processing time (base model)
- **Memory usage**: ~1-2GB peak
- **Disk space**: ~50-100MB for outputs
- **Resumable**: Can interrupt and resume anytime

## 🛑 Interruption & Resume

### Graceful Stop:
- Press `Ctrl+C` anytime during processing
- Partial results are automatically saved
- Resume data saved as `.resume.json`

### Resume (Coming Soon):
```bash
python streamscribe_enhanced.py --resume transcripts/video_name.resume.json
```

## 📁 Output Files

For each video, you get:

```
transcripts/
├── Video_Name_20250929_143000.txt     # Human-readable transcript
├── Video_Name_20250929_143000.json    # Structured data with timestamps
├── Video_Name_20250929_143000.srt     # Subtitle file for video players
└── Video_Name_20250929_143000.resume.json  # Resume data (if interrupted)
```

## 📝 Output Formats

### 1. TXT Format (Live + Final)
```
[00:00:30 - 00:01:00] Welcome to this presentation about artificial intelligence...
[00:01:00 - 00:01:30] In today's session, we'll explore the fundamentals...
```

### 2. JSON Format (Structured)
```json
{
  "video_info": {
    "title": "Video Title",
    "duration": 10800,
    "uploader": "Channel Name"
  },
  "transcripts": [
    {
      "text": "Transcript text here...",
      "start_time": 30.0,
      "end_time": 60.0,
      "chunk_number": 1,
      "language": "en"
    }
  ]
}
```

### 3. SRT Format (Subtitles)
```
1
00:00:30,000 --> 00:01:00,000
Welcome to this presentation about artificial intelligence...

2
00:01:00,000 --> 00:01:30,000
In today's session, we'll explore the fundamentals...
```

## 🔧 Troubleshooting

### Common Issues:

1. **"FFmpeg not found"**
   ```bash
   brew install ffmpeg  # macOS
   ```

2. **Out of memory**
   - Use smaller model (`--model tiny`)
   - Reduce chunk duration (`--chunk-duration 15`)

3. **Slow processing**
   - Use faster model (`--model tiny` or `--model base`)
   - Increase chunk duration (`--chunk-duration 60`)

4. **Poor accuracy**
   - Use better model (`--model small` or `--model medium`)
   - Reduce chunk duration for complex audio
   - Increase overlap (`--overlap 10`)

## 📈 Performance Tips

### For Maximum Speed:
```bash
python streamscribe_enhanced.py "URL" --model tiny --chunk-duration 60 --overlap 0
```

### For Maximum Accuracy:
```bash
python streamscribe_enhanced.py "URL" --model small --chunk-duration 20 --overlap 10
```

### For Balanced Performance:
```bash
python streamscribe_enhanced.py "URL" --model base --chunk-duration 30 --overlap 5
```

## 🎬 Real-time Progress Display

While processing, you'll see:
```
🎤 Transcribing: 45%|████▌     | 23/51 [15:32<18:45, 0.02chunk/s] time=00:11:30 progress=45.2%

⏰ [00:11:30 - 00:12:00] (Chunk #23)
📝 And in conclusion, this demonstrates the importance of proper data preprocessing...
```

## 🛠️ Advanced Usage

### Custom Output Directory:
```bash
python streamscribe_enhanced.py "URL" --output-dir "/path/to/custom/dir"
```

### Processing Multiple Videos:
```bash
# Create a script to process multiple URLs
for url in "URL1" "URL2" "URL3"; do
    python streamscribe_enhanced.py "$url" --model base
done
```