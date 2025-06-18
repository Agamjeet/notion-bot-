import os
import anthropic
import json
from google import genai
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

def print_api_keys():
    """Print API keys (partially masked) to verify they're loaded"""
    claude_key = os.getenv('ANTHROPIC_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    print("\n=== API Keys Status ===")
    if claude_key:
        masked_claude = claude_key[:4] + '*' * (len(claude_key) - 8) + claude_key[-4:]
        print(f"Anthropic API Key: {masked_claude}")
    else:
        print("❌ Anthropic API Key not found!")
        
    if google_key:
        masked_google = google_key[:4] + '*' * (len(google_key) - 8) + google_key[-4:]
        print(f"Google API Key: {masked_google}")
    else:
        print("❌ Google API Key not found!")

def test_claude_api():
    """Test Claude API by sending a simple message"""
    try:
        # Initialize Anthropic client with the correct environment variable
        print(os.getenv('ANTHROPIC_API_KEY'))
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

        # Send a test message using the working configuration
        message = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=1000,
            temperature=1,
            system="You are a world-class poet. Respond only with short poems.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Why is the ocean salty?"
                        }
                    ]
                }
            ]
        )
        
        print("\n=== Claude API Test ===")
        print("Response:", message.content)
        return True
    except Exception as e:
        print("\n=== Claude API Test Failed ===")
        print(f"Error: {str(e)}")
        return False
def test_google_api():
    try:
    

        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

        response = client.models.generate_content(
            model="gemini-2.5-flash", contents="Explain how AI works in a few words"
        )
        print(response.text)
        return True
    except Exception as e:
        print("\n=== Google API Test Failed ===")
        print(f"Error: {str(e)}")
        return False

def main():
    print("Starting API tests...")

    
    # Test Claude API
    # claude_success = test_claude_api()
    google_success = test_google_api()
    # # Test Google Audio Generation API
    # google_success = test_google_audio_generation()
    
    # Print summary
    print("\n=== Test Summary ===")
    # print(f"Claude API Test: {'✅ Success' if claude_success else '❌ Failed'}")
    print(f"Google Audio Generation Test: {'✅ Success' if google_success else '❌ Failed'}")

if __name__ == "__main__":
    main() 