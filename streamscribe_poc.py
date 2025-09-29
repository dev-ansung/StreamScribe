#!/usr/bin/env python3
"""
StreamScribe Proof of Concept

A simple demonstration of real-time audio transcription from YouTube videos.
This POC shows the core functionality without the full architecture.
"""

import sys
import time
import threading
from datetime import datetime
from typing import Optional, Generator
import queue
import argparse

try:
    import yt_dlp
    import whisper
    import numpy as np
    import soundfile as sf
    from io import BytesIO
    import requests
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install required packages:")
    print("pip install yt-dlp openai-whisper numpy soundfile requests")
    sys.exit(1)


class StreamScribePOC:
    """Simple proof of concept for YouTube audio transcription."""
    
    def __init__(self, model_size: str = "base"):
        """Initialize the StreamScribe POC.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.whisper_model = None
        self.audio_queue = queue.Queue()
        self.is_running = False
        
    def load_whisper_model(self):
        """Load the Whisper model for transcription."""
        print(f"Loading Whisper model ({self.model_size})...")
        try:
            self.whisper_model = whisper.load_model(self.model_size)
            print("✅ Whisper model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {e}")
            raise
    
    def extract_youtube_info(self, url: str) -> dict:
        """Extract YouTube video information and audio stream URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary containing video info and audio stream URL
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Find the best audio format
                audio_url = None
                for format_info in info.get('formats', []):
                    if format_info.get('acodec') != 'none':
                        audio_url = format_info.get('url')
                        break
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'audio_url': audio_url,
                    'uploader': info.get('uploader', 'Unknown')
                }
        except Exception as e:
            print(f"❌ Failed to extract YouTube info: {e}")
            raise
    
    def simulate_audio_streaming(self, audio_url: str, chunk_duration: int = 10):
        """Simulate streaming audio by downloading and processing in chunks.
        
        Args:
            audio_url: Direct audio stream URL
            chunk_duration: Duration of each audio chunk in seconds
        """
        print("🎵 Starting audio stream simulation...")
        
        try:
            # For this POC, we'll download the audio and simulate streaming
            # In a real implementation, this would stream directly
            response = requests.get(audio_url, stream=True)
            response.raise_for_status()
            
            # Save to temporary buffer
            audio_data = BytesIO()
            chunk_size = 8192
            downloaded = 0
            
            print("📥 Downloading audio stream...")
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not self.is_running:
                    break
                    
                audio_data.write(chunk)
                downloaded += len(chunk)
                
                # Simulate processing chunks (every 1MB)
                if downloaded % (1024 * 1024) == 0:
                    print(f"📊 Downloaded {downloaded // (1024 * 1024)}MB...")
            
            print("✅ Audio download complete")
            
            # Reset buffer position
            audio_data.seek(0)
            
            # For POC, we'll process the entire audio at once
            # In real implementation, this would be done in streaming chunks
            self.audio_queue.put(audio_data.getvalue())
            
        except Exception as e:
            print(f"❌ Error in audio streaming: {e}")
            self.is_running = False
    
    def transcribe_audio_chunk(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio data using Whisper.
        
        Args:
            audio_data: Raw audio data bytes
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            import tempfile
            import os
            
            # Create a temporary file for the audio data
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe using Whisper
                print("🔊 Running Whisper transcription...")
                result = self.whisper_model.transcribe(temp_file_path)
                transcript = result.get("text", "").strip()
                
                # Also get language detection info if available
                if "language" in result:
                    detected_lang = result.get("language", "unknown")
                    print(f"🌍 Detected language: {detected_lang}")
                
                return transcript if transcript else None
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass  # File might already be deleted
                    
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            print("💡 Make sure FFmpeg is installed: brew install ffmpeg")
            return None
    
    def process_audio_queue(self):
        """Process audio chunks from the queue and transcribe them."""
        print("🎤 Starting transcription processor...")
        
        while self.is_running:
            try:
                # Get audio data from queue (with timeout)
                audio_data = self.audio_queue.get(timeout=1.0)
                
                print("🔄 Processing audio chunk...")
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Transcribe the audio
                transcript = self.transcribe_audio_chunk(audio_data)
                
                if transcript:
                    print(f"\n[{timestamp}] 📝 Transcript:")
                    print(f"'{transcript}'\n")
                else:
                    print(f"[{timestamp}] ⚠️  No speech detected in chunk")
                
                self.audio_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error processing audio: {e}")
    
    def run(self, youtube_url: str):
        """Run the StreamScribe POC.
        
        Args:
            youtube_url: YouTube video URL to transcribe
        """
        print("🚀 Starting StreamScribe POC...")
        print(f"📺 Target URL: {youtube_url}")
        
        try:
            # Load Whisper model
            self.load_whisper_model()
            
            # Extract YouTube info
            print("📋 Extracting video information...")
            video_info = self.extract_youtube_info(youtube_url)
            
            print(f"📹 Video: {video_info['title']}")
            print(f"👤 Uploader: {video_info['uploader']}")
            print(f"⏱️  Duration: {video_info['duration']} seconds")
            
            if not video_info['audio_url']:
                print("❌ No audio stream found")
                return
            
            self.is_running = True
            
            # Start transcription processor in background
            transcription_thread = threading.Thread(
                target=self.process_audio_queue, 
                daemon=True
            )
            transcription_thread.start()
            
            # Start audio streaming (simulated)
            self.simulate_audio_streaming(video_info['audio_url'])
            
            # Wait for processing to complete
            print("⏳ Waiting for transcription to complete...")
            self.audio_queue.join()
            
            print("✅ StreamScribe POC completed!")
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        except Exception as e:
            print(f"❌ POC failed: {e}")
        finally:
            self.is_running = False


def main():
    """Main entry point for the POC."""
    parser = argparse.ArgumentParser(description="StreamScribe POC - YouTube Audio Transcription")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--model", 
        choices=["tiny", "base", "small", "medium", "large"], 
        default="base",
        help="Whisper model size (default: base)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎙️  StreamScribe - Proof of Concept")
    print("=" * 60)
    
    # Create and run POC
    poc = StreamScribePOC(model_size=args.model)
    poc.run(args.url)


if __name__ == "__main__":
    main()