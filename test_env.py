import os
from pathlib import Path
from dotenv import load_dotenv

# Get current directory (should be backend/)
current_dir = Path(__file__).resolve().parent
env_path = current_dir / '.env'

print(f"🔍 Current directory: {current_dir}")
print(f"🔍 Looking for .env at: {env_path}")
print(f"📁 .env file exists: {env_path.exists()}")

if env_path.exists():
    print(f"\n📄 .env file contents (masked):")
    with open(env_path, 'r') as f:
        for line in f:
            if 'GENAI_API_KEY' in line and '=' in line:
                key = line.split('=')[0]
                print(f"{key}=***[HIDDEN]***")
            else:
                print(line.strip())
else:
    print("\n❌ .env file NOT FOUND!")
    print(f"Create it at: {env_path}")

# Load the .env file
load_dotenv(dotenv_path=env_path)

# Check if API key is loaded
api_key = os.getenv("GENAI_API_KEY")
print(f"\n🔑 API Key loaded: {'Yes ✅' if api_key else 'No ❌'}")
if api_key:
    print(f"🔑 API Key length: {len(api_key)}")
    print(f"🔑 First 10 chars: {api_key[:10]}...")
else:
    print("❌ API Key is None or empty!")
    print("\nTroubleshooting:")
    print("1. Make sure .env file exists in backend/ folder")
    print("2. Check the file contains: GENAI_API_KEY=your_key_here")
    print("3. No spaces around the = sign")
    print("4. No quotes around the key")