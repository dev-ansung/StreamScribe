#!/usr/bin/env python3
"""
Test script for StreamScribe Enhanced with long videos
"""

import sys
import os
from streamscribe_enhanced import ChunkedStreamScribe

def test_long_video():
    """Test the enhanced version with a long video."""
    
    # The 3+ hour video from the user
    long_video_url = "https://www.youtube.com/watch?v=k82RwXqZHY8"
    
    print("🧪 StreamScribe Enhanced - Long Video Test")
    print("=" * 50)
    print(f"📺 Testing with: {long_video_url}")
    print("⚠️  This is a LONG video - it will take significant time!")
    print("💡 You can interrupt anytime with Ctrl+C and resume later")
    print()
    
    # Ask for confirmation
    response = input("Continue with long video test? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Test cancelled")
        return
    
    # Ask for model size
    print("\n🤖 Choose Whisper model:")
    print("1. tiny (fastest, least accurate)")
    print("2. base (good balance) - RECOMMENDED")
    print("3. small (better accuracy, slower)")
    
    model_choice = input("Select model (1-3) [2]: ").strip() or "2"
    model_map = {"1": "tiny", "2": "base", "3": "small"}
    model_size = model_map.get(model_choice, "base")
    
    # Ask for chunk duration
    chunk_duration = input("Chunk duration in seconds [30]: ").strip()
    chunk_duration = int(chunk_duration) if chunk_duration.isdigit() else 30
    
    print(f"\n🎬 Starting transcription with:")
    print(f"   Model: {model_size}")
    print(f"   Chunk size: {chunk_duration}s")
    print(f"   Output: transcripts/ directory")
    print()
    
    # Create enhanced scribe
    scribe = ChunkedStreamScribe(
        model_size=model_size,
        chunk_duration=chunk_duration,
        overlap_duration=5
    )
    
    # Run transcription
    scribe.run(long_video_url, "transcripts")

def test_short_video():
    """Test with a shorter video for quick validation."""
    short_urls = [
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo (19s)
        "https://www.youtube.com/watch?v=hFZFjoX2cGg",  # Short talk (~30s)
    ]
    
    print("🧪 StreamScribe Enhanced - Short Video Test")
    print("=" * 50)
    
    url = short_urls[0]  # Use first short video
    print(f"📺 Testing with: {url}")
    
    # Use tiny model for fast testing
    scribe = ChunkedStreamScribe(
        model_size="tiny",
        chunk_duration=10,  # Smaller chunks for short video
        overlap_duration=2
    )
    
    scribe.run(url, "test_transcripts")

def main():
    """Main test function."""
    if len(sys.argv) > 1:
        # Use provided URL
        test_url = sys.argv[1]
        model_size = sys.argv[2] if len(sys.argv) > 2 else "base"
        
        print(f"🧪 Testing StreamScribe Enhanced with custom URL")
        print(f"📺 URL: {test_url}")
        print(f"🤖 Model: {model_size}")
        
        scribe = ChunkedStreamScribe(model_size=model_size)
        scribe.run(test_url, "custom_transcripts")
    else:
        # Interactive menu
        print("🧪 StreamScribe Enhanced Test Suite")
        print("=" * 40)
        print("1. Test with SHORT video (quick validation)")
        print("2. Test with LONG video (3+ hours)")
        print("3. Exit")
        
        choice = input("\nSelect test (1-3): ").strip()
        
        if choice == "1":
            test_short_video()
        elif choice == "2":
            test_long_video()
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()