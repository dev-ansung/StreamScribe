#!/usr/bin/env python3
"""
StreamScribe Enhanced - Real-time chunked audio transcription for long videos

Features:
- Chunked processing for hours-long videos
- Real-time progress updates
- Graceful interruption with resume capability
- Multiple output formats
- Memory-efficient streaming
"""

import sys
import time
import threading
import signal
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Generator, Dict, List, Any
import queue
import argparse
from pathlib import Path

try:
    import yt_dlp
    import whisper
    import numpy as np
    import requests
    from tqdm import tqdm
    import subprocess
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install required packages:")
    print("pip install yt-dlp openai-whisper numpy requests tqdm")
    sys.exit(1)


class ChunkedStreamScribe:
    """Enhanced StreamScribe with chunked processing for long videos."""
    
    def __init__(self, model_size: str = "base", chunk_duration: int = 30, overlap_duration: int = 5):
        """Initialize the enhanced StreamScribe.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            chunk_duration: Duration of each audio chunk in seconds
            overlap_duration: Overlap between chunks in seconds for better accuracy
        """
        self.model_size = model_size
        self.chunk_duration = chunk_duration
        self.overlap_duration = overlap_duration
        self.whisper_model = None
        self.is_running = False
        self.is_interrupted = False
        self.total_duration = 0
        self.processed_duration = 0
        self.transcripts = []
        self.output_file = None
        self.progress_bar = None
        
        # Set up signal handlers for graceful interruption
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully."""
        print(f"\n🛑 Received interrupt signal ({signum})")
        self.is_interrupted = True
        self.is_running = False
        if self.progress_bar:
            self.progress_bar.close()
        self._save_partial_results()
        print("📝 Partial results saved. You can resume later.")
        sys.exit(0)
        
    def load_whisper_model(self):
        """Load the Whisper model for transcription."""
        print(f"🤖 Loading Whisper model ({self.model_size})...")
        try:
            self.whisper_model = whisper.load_model(self.model_size)
            print("✅ Whisper model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {e}")
            raise
    
    def extract_youtube_info(self, url: str) -> Dict[str, Any]:
        """Extract YouTube video information and audio stream URL."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'extract_flat': False,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("📋 Extracting video information...")
                info = ydl.extract_info(url, download=False)
                
                # Find the best audio format
                audio_url = None
                for format_info in info.get('formats', []):
                    if format_info.get('acodec') != 'none':
                        audio_url = format_info.get('url')
                        break
                
                duration = info.get('duration', 0)
                self.total_duration = duration
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': duration,
                    'audio_url': audio_url,
                    'uploader': info.get('uploader', 'Unknown'),
                    'description': info.get('description', '')[:200] + '...' if info.get('description') else ''
                }
        except Exception as e:
            print(f"❌ Failed to extract YouTube info: {e}")
            raise
    
    def create_audio_chunks(self, audio_url: str) -> Generator[bytes, None, None]:
        """Create audio chunks using FFmpeg for efficient streaming."""
        print("🎵 Starting chunked audio processing...")
        
        # Calculate chunk parameters
        chunk_size = self.chunk_duration
        overlap_size = self.overlap_duration
        step_size = chunk_size - overlap_size
        
        current_position = 0
        chunk_number = 0
        
        while current_position < self.total_duration and self.is_running:
            if self.is_interrupted:
                break
                
            # Calculate actual chunk duration (handle end of video)
            actual_duration = min(chunk_size, self.total_duration - current_position)
            
            try:
                # Use FFmpeg to extract audio chunk
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-ss', str(current_position),
                    '-i', audio_url,
                    '-t', str(actual_duration),
                    '-vn',  # No video
                    '-acodec', 'pcm_s16le',  # PCM 16-bit
                    '-ar', '16000',  # 16kHz sample rate (Whisper's preferred)
                    '-ac', '1',  # Mono
                    '-f', 'wav',  # WAV format
                    '-',  # Output to stdout
                ]
                
                process = subprocess.Popen(
                    ffmpeg_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=0
                )
                
                # Read the audio data
                audio_data, stderr = process.communicate()
                
                if process.returncode != 0:
                    print(f"⚠️ FFmpeg warning for chunk {chunk_number}: {stderr.decode()}")
                    current_position += step_size
                    continue
                
                if len(audio_data) > 0:
                    yield {
                        'data': audio_data,
                        'start_time': current_position,
                        'duration': actual_duration,
                        'chunk_number': chunk_number
                    }
                
                chunk_number += 1
                current_position += step_size
                self.processed_duration = current_position
                
            except Exception as e:
                print(f"❌ Error processing chunk {chunk_number}: {e}")
                current_position += step_size
                continue
    
    def transcribe_audio_chunk(self, chunk_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transcribe a single audio chunk."""
        try:
            import tempfile
            
            # Create temporary file for the chunk
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(chunk_data['data'])
                temp_file_path = temp_file.name
            
            try:
                # Transcribe using Whisper
                result = self.whisper_model.transcribe(
                    temp_file_path,
                    temperature=0.0,  # More deterministic output
                    no_speech_threshold=0.6,  # Skip chunks with no speech
                    condition_on_previous_text=False  # Independent chunks
                )
                
                transcript = result.get("text", "").strip()
                
                if not transcript:
                    return None
                
                return {
                    'text': transcript,
                    'start_time': chunk_data['start_time'],
                    'end_time': chunk_data['start_time'] + chunk_data['duration'],
                    'duration': chunk_data['duration'],
                    'chunk_number': chunk_data['chunk_number'],
                    'language': result.get('language', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                }
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
                    
        except Exception as e:
            print(f"❌ Transcription error for chunk {chunk_data.get('chunk_number', 'unknown')}: {e}")
            return None
    
    def format_time(self, seconds: float) -> str:
        """Format seconds into HH:MM:SS format."""
        return str(timedelta(seconds=int(seconds)))
    
    def save_transcript(self, transcript: Dict[str, Any], format_type: str = "live"):
        """Save transcript in real-time."""
        if not self.output_file:
            return
            
        if format_type == "live":
            # Real-time console output
            start_time = self.format_time(transcript['start_time'])
            end_time = self.format_time(transcript['end_time'])
            
            print(f"\n⏰ [{start_time} - {end_time}] (Chunk #{transcript['chunk_number']})")
            print(f"📝 {transcript['text']}")
            
            # Also save to file
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(f"[{start_time} - {end_time}] {transcript['text']}\n")
        
        # Add to internal transcript list
        self.transcripts.append(transcript)
    
    def _save_partial_results(self):
        """Save partial results when interrupted."""
        if not self.transcripts:
            return
            
        # Save as JSON for resuming
        resume_file = f"{self.output_file}.resume.json"
        resume_data = {
            'transcripts': self.transcripts,
            'processed_duration': self.processed_duration,
            'total_duration': self.total_duration,
            'interrupted_at': datetime.now().isoformat()
        }
        
        with open(resume_file, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resume data saved to: {resume_file}")
    
    def save_final_results(self, video_info: Dict[str, Any]):
        """Save final results in multiple formats."""
        if not self.transcripts:
            print("⚠️ No transcripts to save")
            return
        
        base_name = self.output_file.replace('.txt', '')
        
        # Save as JSON
        json_file = f"{base_name}.json"
        json_data = {
            'video_info': video_info,
            'transcripts': self.transcripts,
            'processing_info': {
                'model_size': self.model_size,
                'chunk_duration': self.chunk_duration,
                'overlap_duration': self.overlap_duration,
                'total_chunks': len(self.transcripts),
                'processed_at': datetime.now().isoformat()
            }
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # Save as SRT subtitle format
        srt_file = f"{base_name}.srt"
        with open(srt_file, 'w', encoding='utf-8') as f:
            for i, transcript in enumerate(self.transcripts, 1):
                start_time = self._seconds_to_srt_time(transcript['start_time'])
                end_time = self._seconds_to_srt_time(transcript['end_time'])
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{transcript['text']}\n\n")
        
        print(f"💾 Results saved:")
        print(f"   📄 Text: {self.output_file}")
        print(f"   📊 JSON: {json_file}")
        print(f"   🎬 SRT: {srt_file}")
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def run(self, youtube_url: str, output_dir: str = "transcripts"):
        """Run the enhanced StreamScribe with chunked processing."""
        print("🚀 Starting Enhanced StreamScribe...")
        print(f"📺 Target URL: {youtube_url}")
        
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Load Whisper model
            self.load_whisper_model()
            
            # Extract video info
            video_info = self.extract_youtube_info(youtube_url)
            
            print(f"📹 Video: {video_info['title']}")
            print(f"👤 Uploader: {video_info['uploader']}")
            print(f"⏱️  Duration: {self.format_time(video_info['duration'])}")
            print(f"🧩 Chunk size: {self.chunk_duration}s (overlap: {self.overlap_duration}s)")
            
            if not video_info['audio_url']:
                print("❌ No audio stream found")
                return
            
            # Setup output file
            safe_title = "".join(c for c in video_info['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title[:50]  # Limit filename length
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_file = os.path.join(output_dir, f"{safe_title}_{timestamp}.txt")
            
            # Initialize progress bar
            total_chunks = int(self.total_duration / (self.chunk_duration - self.overlap_duration)) + 1
            self.progress_bar = tqdm(
                total=total_chunks,
                desc="🎤 Transcribing",
                unit="chunk",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
            )
            
            self.is_running = True
            
            # Process chunks
            for chunk_data in self.create_audio_chunks(video_info['audio_url']):
                if not self.is_running or self.is_interrupted:
                    break
                
                # Update progress
                progress_percent = (self.processed_duration / self.total_duration) * 100 if self.total_duration > 0 else 0
                elapsed_time = self.format_time(self.processed_duration)
                
                self.progress_bar.set_postfix({
                    'time': elapsed_time,
                    'progress': f"{progress_percent:.1f}%"
                })
                
                # Transcribe chunk
                transcript = self.transcribe_audio_chunk(chunk_data)
                
                if transcript:
                    self.save_transcript(transcript)
                
                self.progress_bar.update(1)
            
            self.progress_bar.close()
            
            if not self.is_interrupted:
                print("✅ Transcription completed successfully!")
                self.save_final_results(video_info)
            else:
                print("⏹️ Transcription interrupted by user")
                
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
            self.is_interrupted = True
        except Exception as e:
            print(f"❌ Enhanced StreamScribe failed: {e}")
        finally:
            self.is_running = False
            if self.progress_bar:
                self.progress_bar.close()


def main():
    """Main entry point for the enhanced POC."""
    parser = argparse.ArgumentParser(description="StreamScribe Enhanced - Chunked YouTube Audio Transcription")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--model", 
        choices=["tiny", "base", "small", "medium", "large"], 
        default="base",
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "--chunk-duration",
        type=int,
        default=30,
        help="Duration of each audio chunk in seconds (default: 30)"
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=5,
        help="Overlap between chunks in seconds (default: 5)"
    )
    parser.add_argument(
        "--output-dir",
        default="transcripts",
        help="Output directory for transcripts (default: transcripts)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎙️  StreamScribe Enhanced - Chunked Processing")
    print("=" * 60)
    
    # Create and run enhanced StreamScribe
    scribe = ChunkedStreamScribe(
        model_size=args.model,
        chunk_duration=args.chunk_duration,
        overlap_duration=args.overlap
    )
    scribe.run(args.url, args.output_dir)


if __name__ == "__main__":
    main()