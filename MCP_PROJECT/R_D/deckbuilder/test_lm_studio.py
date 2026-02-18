#!/usr/bin/env python3
"""
Simple test script to verify LM Studio connection and API format.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lm_studio_client import LMStudioClient

def test_lm_studio_connection():
    """Test LM Studio connection and basic functionality."""
    print("Testing LM Studio connection...")
    
    client = LMStudioClient()
    
    # Test connection
    if client.test_connection():
        print("✅ Successfully connected to LM Studio")
    else:
        print("❌ Failed to connect to LM Studio")
        return False
    
    # Test getting models
    try:
        models = client.get_models()
        print(f"Available models: {models}")
    except Exception as e:
        print(f"Error getting models: {e}")
        return False
    
    # Test a simple chat completion
    try:
        print("Testing chat completion...")
        messages = [
            {"role": "user", "content": "Hello, what is Magic: The Gathering?"}
        ]
        
        response_chunks = []
        for chunk in client.chat_completion(
            messages=messages,
            model="gpt-oss-20b",
            max_tokens=100,
            temperature=0.7,
            stream=False
        ):
            response_chunks.append(chunk)
        
        response = "".join(response_chunks)
        print(f"Response: {response[:100]}...")
        print("✅ Chat completion test successful")
        return True
        
    except Exception as e:
        print(f"❌ Chat completion failed: {e}")
        return False

if __name__ == "__main__":
    test_lm_studio_connection()