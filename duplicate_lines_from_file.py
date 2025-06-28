import argparse
from pathlib import Path

def remove_duplicate_lines(file_path: Path):
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist.")
        return

    seen = set()
    unique_lines = []

    with file_path.open('r', encoding='utf-8') as file:
        for line in file:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)

    with file_path.open('w', encoding='utf-8') as file:
        file.writelines(unique_lines)

    print(f"Duplicate lines removed from '{file_path}'.")

def main():
    # parser = argparse.ArgumentParser(description="Remove duplicate lines from a text file.")
    # parser.add_argument('file', type=str, help="Path to the input text file")
    # args = parser.parse_args()

    # file_path = Path(args.file)
    file_path = Path(r'C:\Personal\Developed\Hailuio\files\gemni.txt')  # Replace with your file path
    remove_duplicate_lines(file_path)
    file_path = Path(r'C:\Personal\Developed\Hailuio\files\brapanty_fantasy.txt')  # Replace with your file path
    remove_duplicate_lines(file_path)
    file_path = Path(r'C:\Personal\Developed\Hailuio\files\oldnews.txt')  # Replace with your file path
    remove_duplicate_lines(file_path)

if __name__ == '__main__':
    main()
