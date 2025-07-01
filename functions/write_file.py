import os

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
