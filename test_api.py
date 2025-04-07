import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "llama-3.2-11b-vision-preview",
    "messages": [
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ]
}

print("API Key:", "*" * len(api_key[:-4]) + api_key[-4:])
print("\nHeaders being sent:")
print(json.dumps(headers, indent=2))
print("\nRequest URL:", url)
print("\nRequest data:")
print(json.dumps(data, indent=2))
print("\nMaking request...")

response = requests.post(url, headers=headers, json=data)
print(f"\nResponse status: {response.status_code}")
print(f"Response content: {response.text}") 