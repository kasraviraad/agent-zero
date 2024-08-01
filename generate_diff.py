import os
import difflib

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

def read_merged_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    
    files = {}
    current_file = None
    current_content = []

    for line in content.split('\n'):
        if line.startswith('# File: '):
            if current_file:
                files[current_file] = '\n'.join(current_content)
            current_file = line[8:].strip()
            current_content = []
        elif current_file:
            current_content.append(line)

    if current_file:
        files[current_file] = '\n'.join(current_content)

    return files

def get_current_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return None

def generate_diff_report(merged_content, source_dir, max_file_changes=10, max_report_size=10000):
    diffs = []
    total_report_size = 0

    for filepath, old_content in merged_content.items():
        if not is_relevant_file(filepath):
            continue

        current_file = os.path.join(source_dir, filepath)
        current_content = get_current_file_content(current_file)

        if old_content.strip() != current_content.strip():
            diff = list(difflib.unified_diff(
                old_content.splitlines(keepends=True),
                current_content.splitlines(keepends=True),
                fromfile=f'merged_relevant_files.txt/{filepath}',
                tofile=f'current/{filepath}',
                n=3  # Number of context lines
            ))

            if any(line.startswith(('+', '-')) for line in diff):
                diffs.append((filepath, ''.join(diff).strip()))
                total_report_size += len(''.join(diff).strip()) + len(filepath) + 2  # 2 for the newlines

        if len(diffs) >= max_file_changes or total_report_size >= max_report_size:
            break

    return diffs

def write_diff_to_file(diffs, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for filepath, diff in diffs:
            if diff:
                file.write(f"File: {filepath}\n{diff}\n\n")

def main():
    source_dir = os.getcwd()
    merged_content = read_merged_file('merged_relevant_files.txt')
    diffs = generate_diff_report(merged_content, source_dir, max_file_changes=10, max_report_size=10000)
    write_diff_to_file(diffs, 'recent_changes.txt')

    print(f"Diff report generated in 'recent_changes.txt'")
    print(f"Number of files with significant changes: {len(diffs)}")

if __name__ == "__main__":
    main()