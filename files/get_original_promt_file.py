import argparse
import os
from pathlib import Path
import re
import sys

maind_dir = r'C:\Personal\Developed\Hailuio\files\gemini'

def main():
    parser = argparse.ArgumentParser(description="Open a file and apply regex to its contents.")
    parser.add_argument('filename', help='Path to the file')
    # parser.add_argument('pattern', help='Regex pattern to search in the file')
    args = parser.parse_args()
    pattern = r'(.*)(_\w+_\d+)'
    st = args.filename
    new_name = st.replace(re.search(pattern, st).group(2),'') + '.txt'
    # breakpoint()
    ftoopen = Path(maind_dir, new_name)
    os.system(f'code "{str(ftoopen)}"')
    

if __name__ == "__main__":
    main()