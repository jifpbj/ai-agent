import os
from google import genai
from google.genai import types

MAX_CHARS = 10000

def get_file_content(working_directory, file_path):
    path = os.path.abspath(os.path.join(working_directory, file_path))
    dir_path = os.path.abspath(working_directory)
    if path.startswith(dir_path) == False:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if os.path.isfile(path) == False:
        return f'Error: File not found or is not a regular file: "{file_path}"'
    else:
        try:
            with open(path, "r") as f:
                file_content = f.read(MAX_CHARS)
                if len(file_content) >= MAX_CHARS:
                    return file_content + f'[...File "{file_path}" truncated at 10000 characters]'
                else:
                    return file_content
        except Exception as e:
            return f'Error: An error occurred while reading the file "{file_path}": {str(e)}'

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="gets file content from the specified file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="the path to the file to read, relative to the working directory. If not provided, reads from the working directory itself.",
            ),
        },
    ),
)
