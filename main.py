import os
import base64
import openai
from dotenv import load_dotenv
import subprocess
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up the screenshot path
timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
screenshot_path = os.path.expanduser(f"~/Pictures/Screenshots/eyeQ/screenshot_{timestamp}.png")

# 1. Capture the screenshot
subprocess.run(f"slurp | grim -g - {screenshot_path}", shell=True)

# 2. Check if the screenshot was created successfully
if not os.path.exists(screenshot_path):
    print("Failed to take screenshot.")
    exit(1)

print(f"Screenshot saved at: {screenshot_path}")

# 3. Use wofi to get the user prompt
prompt_command = "echo 'Enter your question about the screenshot:' | wofi -d -p 'Prompt'"
prompt_process = subprocess.run(prompt_command, shell=True, capture_output=True, text=True)
prompt = prompt_process.stdout.strip()  # Read the prompt entered by the user

if not prompt:
    print("No prompt entered. Exiting.")
    exit(1)

print(f"Prompt: {prompt}")

# encode the image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

base64_image = encode_image(screenshot_path)

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",  # Replace with the correct model supporting image + text
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}",  # Adjust for .png image
                        "detail": "low"
                    },
                },
            ],
        }
    ],
    max_tokens=300,
)

ans = response.choices[0].message.content
print(ans)

wofi_command = f"echo '{ans}' | wofi -d -p 'Answer'"
# print(wofi_command)
subprocess.run(wofi_command, shell=True)
