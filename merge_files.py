import os

def is_relevant_file(file_path):
    # List of relevant file extensions
    relevant_extensions = ['.py', '.js', '.ts', '.html', '.css', '.json', '.yml', '.yaml', '.md', '.txt']
    # List of relevant file names
    relevant_files = ['Dockerfile', '.gitignore', '.env.example', 'requirements.txt', 'package.json']
    # List of relevant directories
    relevant_dirs = ['prompts']
    
    file_extension = os.path.splitext(file_path)[1]
    file_name = os.path.basename(file_path)
    dir_name = os.path.basename(os.path.dirname(file_path))
    
    return (file_extension.lower() in relevant_extensions or 
            file_name in relevant_files or 
            dir_name in relevant_dirs)

def merge_files(directory, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories and common non-code directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
            
            for file in files:
                if file == output_file:
                    continue  # Skip the output file itself
                file_path = os.path.join(root, file)
                if is_relevant_file(file_path):
                    relative_path = os.path.relpath(file_path, directory)
                    outfile.write(f"\n\n# File: {relative_path}\n")
                    outfile.write("#" + "=" * 78 + "\n\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except UnicodeDecodeError:
                        outfile.write(f"# Unable to read file: {relative_path} (possibly binary)\n")

# Set the directory to the current working directory (root of your GitHub project)
directory = os.getcwd()
output_file = 'merged_relevant_files.txt'

merge_files(directory, output_file)
print(f"Relevant files have been merged into {output_file}")