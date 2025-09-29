#!/usr/bin/env python3
"""
StreamScribe POC Test Script

Simple test to verify the POC works with a short YouTube video.
"""

import os
import sys
from streamscribe_poc import StreamScribePOC

def test_poc():
    """Test the StreamScribe POC with a sample video."""
    
    # Sample YouTube URLs for testing (short videos work best for POC)
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll (classic test)
        "https://www.youtube.com/watch?v=jNQXAC9IVRw"   # "Me at the zoo" (first YouTube video)
    ]
    
    print("🧪 StreamScribe POC Test")
    print("=" * 40)
    
    # Use the first test URL
    test_url = test_urls[1]  # Using "Me at the zoo" as it's very short
    
    print(f"📺 Testing with: {test_url}")
    print("ℹ️  Note: This POC will download the entire audio file for demonstration.")
    print("ℹ️  In a real implementation, this would stream in real-time chunks.\n")
    
    # Create POC instance with a smaller model for faster testing
    poc = StreamScribePOC(model_size="tiny")
    
    try:
        poc.run(test_url)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    if len(sys.argv) > 1:
        # Use provided URL
        test_url = sys.argv[1]
        model_size = sys.argv[2] if len(sys.argv) > 2 else "tiny"
        
        print(f"🧪 Testing StreamScribe POC with custom URL")
        print(f"📺 URL: {test_url}")
        print(f"🤖 Model: {model_size}")
        
        poc = StreamScribePOC(model_size=model_size)
        poc.run(test_url)
    else:
        # Run default test
        test_poc()

if __name__ == "__main__":
    main()