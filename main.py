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
def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    function_name_str = function_call_part.name
    function_args = function_call_part.args

    function_to_call = function_mapping.get(function_name_str)
    try:
        # Assuming all functions in your mapping take working_directory
        # Adjust if some functions don't need it.
        function_result = function_to_call(working_directory="./calculator/", **function_args)
    except Exception as e:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name_str,
                    response={"error": f"Error executing {function_name_str}: {e}"},
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
user_prompt = args.content  # get content from argparse cmd line
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

MAX_LOOP = 20  # Safeguard to prevent infinite loops

## Generate Content ##
def generate_content_loop(model_name, conversation_messages, system_instruction):
    current_loop = 0
    while current_loop < MAX_LOOP:
        current_loop += 1
        if args.verbose:
            print(f"\n--- Loop {current_loop} ---")
            print("Sending messages to model:")
            for msg in conversation_messages:
                print(f"  {msg.role}: {msg.parts[0].text if msg.parts and msg.parts[0].text else msg.parts[0].function_call.name if msg.parts and msg.parts[0].function_call else 'Function Response'}")

        response = client.models.generate_content(
            model=model_name,
            contents=conversation_messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_instruction
            )
        )

        if args.verbose:
            metadata = response.usage_metadata
            print("Prompt tokens:", metadata.prompt_token_count)
            print("Response tokens:", metadata.candidates_token_count)
            print("Model response received.")
            if response.text:
                print("Model text response:", response.text)
            if response.function_calls:
                print("Model requested function calls:")
                for fc in response.function_calls:
                    print(f"  - {fc.name}({fc.args})")

        # Add the model's response to the conversation history
        # If the model has a text response in its candidates, add that.
        # Otherwise, if it has function calls, add those.
        # It's important to add the model's *intent* to the history before executing functions.
        for candidate in response.candidates:
            if candidate.content:
                conversation_messages.append(candidate.content)

        ## Call functions if any are requested in the response ##
        if response.function_calls:
            for function_call_part in response.function_calls:
                function_call_result = call_function(function_call_part, args.verbose)
                if function_call_result.parts[0].function_response.response:
                    if args.verbose:
                        print(f"Function {function_call_part.name} response: {function_call_result.parts[0].function_response.response}")
                    # Add the function's *result* to the conversation history
                    conversation_messages.append(function_call_result)
                else:
                    raise Exception("No response from function call")
        else:
            # If no function calls, the model has likely provided its final text response.
            # Print the final text and break the loop.
            if response.text:
                print("\nFinal Model Response:")
                print(response.text)
            else:
                print("\nModel did not provide a text response or function call in this turn.")
            break # Exit the loop if no more function calls

    if current_loop >= MAX_LOOP:
        print(f"\nWarning: Maximum loop limit ({MAX_LOOP}) reached. Conversation may be incomplete.")

# Start the looped content generation
generate_content_loop(model, messages, system_prompt)
