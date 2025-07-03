import os
from google import genai
from google.genai import types

def get_files_info(working_directory, directory=None):
    # Ensure directory is not None for os.path.join
    if directory is None:
        directory = ""

    print(f"Working directory: {working_directory}")
    combined_path = os.path.join(working_directory, directory)
    dir_path = os.path.abspath(combined_path)
    print(f"abs_path of '{directory}': {dir_path} ")

    # Security check: Ensure the requested path is within the working directory
    if not dir_path.startswith(os.path.abspath(working_directory)):
        return {"error": f'Cannot list "{directory}" as it is outside the permitted working directory.'}

    if not os.path.isdir(dir_path):
        return {"error": f'"{directory}" is not a directory.'}
    else:
        file_list = []
        try:
            items = os.listdir(dir_path)
            print(f"Listing files in '{directory}': {items}") # This print is fine for debugging

            for item in items:
                item_path = os.path.join(dir_path, item)
                try:
                    is_dir = os.path.isdir(item_path)
                    file_size = os.path.getsize(item_path) if not is_dir else None # Size only for files
                    file_list.append({
                        "name": item,
                        "is_directory": is_dir,
                        "size_bytes": file_size,
                    })
                except OSError as e:
                    # Handle cases where we can't get info for a specific item (e.g., permissions)
                    file_list.append({
                        "name": item,
                        "error": f"Could not get info: {e}"
                    })
            return {"files": file_list}
        except OSError as e:
            return {"error": f"Error listing directory '{directory}': {e}"}


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)
