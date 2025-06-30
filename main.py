import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

## Setup environment variables ##
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

## Check if arguments are provided ##
if len(sys.argv) == 1:
    print("Error: Please provide the contents to generate.")
    sys.exit(1)


## Add verbose flag ##
parser = argparse.ArgumentParser(description="Generate content using Gemini API.")
parser.add_argument("content", type=str, help="Content to generate")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()



## Message to send to the model ##
model = "gemini-2.0-flash-001"
user_prompt = args.content #get content from argparse cmd line
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

response = client.models.generate_content(
    model=model,
    contents=messages,
)
print(response.text)

if args.verbose:
    metadata = response.usage_metadata
    print("User prompt:", args.content)
    print("Prompt tokens:", metadata.prompt_token_count)
    print("Response tokens:", metadata.candidates_token_count)
