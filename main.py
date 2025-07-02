import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python import schema_run_python_file, run_python_file

## Setup environment variables ##
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

## System prompt
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read the content of a file
- write the content of a file
- Run python files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

## Check if arguments are provided ##
if len(sys.argv) == 1:
    print("Error: Please provide the contents to generate.")
    sys.exit(1)

## Add verbose flag ##
parser = argparse.ArgumentParser(description="Generate content using Gemini API.")
parser.add_argument("content", type=str, help="Content to generate")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

## Function declaration for get_files_info ##
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_run_python_file,
        schema_write_file,
        schema_get_file_content,
    ]
)

# Map string function names to actual functions
function_mapping = {
"write_file": write_file,
"run_python_file": run_python_file,
"get_files_info": get_files_info,
"get_file_content": get_file_content,

}

## Calling Functions
def call_function(function_call_part, verbose = False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    function_name_str = function_call_part.name
    function_args = function_call_part.args

    function_to_call = function_mapping.get(function_name_str)
    try:
        function_result = function_to_call( working_directory="./calculator/", **function_args)
    except Exception as e:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name_str,
                    response={"error": f"Unknown function: {function_name_str}"},
                )
            ],
        )
    return types.Content(
    role="tool",
    parts=[
        types.Part.from_function_response(
            name=function_name_str,
            response={"result": function_result},
        )
    ],
)


## Message to send to the model ##
model = "gemini-2.0-flash-001"
user_prompt = args.content #get content from argparse cmd line
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]


## Generate Content ##
response = client.models.generate_content(
    model=model,
    contents=messages,
    config = types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt
    )
)

if response.function_calls:
    for function_call_part in response.function_calls:
        function_call_result = call_function(function_call_part)
        if function_call_result.parts[0].function_response.response:
            print(f"Function {function_call_part.name} response: {function_call_result.parts[0].function_response.response}")
        else:
            raise Exception("no response from function call")
else:
    print(response.text)

if args.verbose:
    metadata = response.usage_metadata
    print("User prompt:", args.content)
    print("Prompt tokens:", metadata.prompt_token_count)
    print("Response tokens:", metadata.candidates_token_count)
