import os

def get_files_info(working_directory, directory=None):
    print(f"Working directory: {working_directory}")
    combined_path = os.path.join(working_directory, directory)
    dir_path = os.path.abspath(combined_path)
    print(f"abs_path of '{directory}': {dir_path} ")


    if dir_path.startswith(os.path.abspath(working_directory)) == False:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if os.path.isdir(dir_path) == False:
        return f'Error: "{directory}" is not a directory'
    else:
        list = os.listdir(dir_path)
        print(f"Listing files in '{directory}': {list}")
        for value in list:
            value_path = os.path.join(dir_path, value)
            print(f"- {value}: file_size={os.path.getsize(value_path)} bytes, is_dir={os.path.isdir(value_path)}")
        return




