import os
import re

def get_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_abs_path(*relative_paths):
    return os.path.join(get_base_dir(), *relative_paths)

def read_file(relative_path, **kwargs):
    absolute_path = get_abs_path(relative_path)
    try:
        with open(absolute_path, 'r', encoding='utf-8') as f:
            content = remove_code_fences(f.read())

        # Replace placeholders with values from kwargs
        for key, value in kwargs.items():
            placeholder = "{{" + key + "}}"
            strval = str(value)
            content = content.replace(placeholder, strval)

        return content
    except FileNotFoundError:
        print(f"File not found: {absolute_path}")
        raise

def remove_code_fences(text):
    return re.sub(r'~~~\w*\n|~~~', '', text)

def exists(*relative_paths):
    path = get_abs_path(*relative_paths)
    return os.path.exists(path)