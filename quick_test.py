#!/usr/bin/env python3
"""
Quick test script for StreamScribe POC with different videos
"""

import sys
from streamscribe_poc import StreamScribePOC

def main():
    # Test URLs (short videos recommended for testing)
    test_videos = [
        {
            "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "name": "Me at the zoo (first YouTube video)",
            "duration": "19 seconds"
        },
        {
            "url": "https://www.youtube.com/watch?v=hFZFjoX2cGg",
            "name": "Alan Watts - Short Talk",
            "duration": "~30 seconds"
        }
    ]
    
    print("🎯 StreamScribe POC - Quick Test")
    print("=" * 50)
    
    # Choose video
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
        model_size = sys.argv[2] if len(sys.argv) > 2 else "tiny"
    else:
        print("📺 Available test videos:")
        for i, video in enumerate(test_videos, 1):
            print(f"{i}. {video['name']} ({video['duration']})")
        
        try:
            choice = int(input("\nSelect video (1-2) or press Enter for default: ") or "1")
            video_url = test_videos[choice - 1]["url"]
        except (ValueError, IndexError):
            video_url = test_videos[0]["url"]
        
        model_size = input("Model size (tiny/base/small) [tiny]: ").strip() or "tiny"
    
    print(f"\n🎬 Testing with: {video_url}")
    print(f"🤖 Using model: {model_size}")
    print()
    
    # Run transcription
    poc = StreamScribePOC(model_size=model_size)
    poc.run(video_url)

if __name__ == "__main__":
    main()