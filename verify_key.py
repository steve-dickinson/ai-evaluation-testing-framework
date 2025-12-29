import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENAI_API_KEY")
print(f"Testing key: {key[:5]}...{key[-5:] if key else 'None'}")

if not key:
    print("No key found!")
    exit(1)

try:
    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=5
    )
    print("Success:", response.choices[0].message.content)
except Exception as e:
    print("Error:", e)
