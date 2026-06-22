#!/usr/bin/env python3
"""
NEXKEY — LM Studio Connection Test
Verifies that LM Studio is running and accessible for agent inference.
"""

import urllib.request
import urllib.error
import json
import sys
import time
from pathlib import Path

# Load config
def load_config():
    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    try:
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        print("⚠️  PyYAML not installed. Using default config.")
        return {
            "lm_studio": {
                "host": "localhost",
                "port": 1234,
                "api_url": "http://localhost:1234/v1"
            }
        }

def test_lm_studio_connection():
    """Test if LM Studio is running and accessible"""
    config = load_config()
    lm_config = config.get('lm_studio', {})
    
    api_url = lm_config.get('api_url', 'http://localhost:1234/v1')
    host = lm_config.get('host', 'localhost')
    port = lm_config.get('port', 1234)
    
    print(f"🔍 Testing LM Studio connection...")
    print(f"   Host: {host}:{port}")
    print(f"   API URL: {api_url}")
    print()
    
    # Test 1: Check if server is running
    try:
        url = f"{api_url}/models"
        req = urllib.request.Request(url, method='GET')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read())
                models = data.get('data', [])
                
                print("✅ LM Studio is RUNNING")
                print(f"   Found {len(models)} model(s):")
                for model in models:
                    model_id = model.get('id', 'unknown')
                    print(f"   - {model_id}")
                return True
            else:
                print(f"❌ LM Studio returned status {response.status}")
                return False
                
    except urllib.error.URLError as e:
        print(f"❌ Cannot connect to LM Studio")
        print(f"   Error: {e.reason}")
        print()
        print("📋 To fix this:")
        print("   1. Open LM Studio")
        print("   2. Go to 'Local Server' tab")
        print("   3. Click 'Start Server'")
        print("   4. Make sure port 1234 is available")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_inference():
    """Test actual inference with LM Studio"""
    config = load_config()
    lm_config = config.get('lm_studio', {})
    
    api_url = lm_config.get('api_url', 'http://localhost:1234/v1')
    model = lm_config.get('model', 'llama-3.3-70b-instruct')
    
    print()
    print(f"🧪 Testing inference with model: {model}")
    
    # Test prompt in Spanish
    test_prompt = "Eres un asistente de NEXKEY, una empresa de automatización con IA para el sector inmobiliario. Responde brevemente: ¿qué haces?"
    
    try:
        url = f"{api_url}/chat/completions"
        data = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": "Eres un asistente de NEXKEY, especializado en automatización para inmobiliarias."},
                {"role": "user", "content": test_prompt}
            ],
            "max_tokens": lm_config.get('max_tokens', 1024),
            "temperature": lm_config.get('temperature', 0.7)
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=60) as response:
            if response.status == 200:
                result = json.loads(response.read())
                content = result['choices'][0]['message']['content']
                
                print("✅ Inference test PASSED")
                print(f"   Response: {content[:200]}...")
                return True
            else:
                print(f"❌ Inference failed with status {response.status}")
                return False
                
    except Exception as e:
        print(f"❌ Inference test failed: {e}")
        return False

def main():
    print("=" * 50)
    print("NEXKEY — LM Studio Connection Test")
    print("=" * 50)
    print()
    
    # Test connection
    connection_ok = test_lm_studio_connection()
    
    if connection_ok:
        # Test inference
        inference_ok = test_inference()
        
        if inference_ok:
            print()
            print("🎉 LM Studio is ready for NEXKEY agents!")
            print("   You can now run: python3 scripts/orchestrate.py --mode live")
        else:
            print()
            print("⚠️  Connection OK but inference failed")
            print("   Check your model name in config/settings.yaml")
    else:
        print()
        print("❌ LM Studio is not running")
        print("   Start LM Studio and try again")
    
    return 0 if (connection_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
