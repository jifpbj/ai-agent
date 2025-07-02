import os
from google import genai
from google.genai import types

def write_file(working_directory, file_path, content):
    path = os.path.abspath(os.path.join(working_directory, file_path))
    dir_path = os.path.abspath(working_directory)
    
    if not path.startswith(dir_path):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    try:
        with open(path, "w") as f:
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error: An error occurred while writing to the file "{file_path}": {str(e)}'

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="writes file content to the specified file_path, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="the path to the file to write to, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="the content to write to the file.",
            )
        },
    ),
)
