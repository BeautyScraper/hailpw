import re
from pathlib import Path

import re
from pathlib import Path

def bulk_rename_files(directory, pattern, replacement, file_filter="*.*", dry_run=True):
    """
    Renames files in the given directory using a regex pattern and avoids overwriting by adding suffixes.

    Parameters:
    - directory (str or Path): The directory containing files.
    - pattern (str): The regex pattern to match in filenames.
    - replacement (str): The replacement string using re.sub rules.
    - file_filter (str): Glob pattern to filter files.
    - dry_run (bool): If True, just prints what would be renamed.

    Returns:
    - renamed_files (list of tuples): (original_name, new_name)
    """
    path = Path(directory)
    renamed_files = []

    for file in path.glob(file_filter):
        if file.is_file():
            new_name = re.sub(pattern, replacement, file.name)
            target = file.with_name(new_name)
            counter = 1

            # Avoid overwriting existing files
            while target.exists():
                stem = target.stem
                suffix = target.suffix
                new_name = f"{stem}_c{counter}{suffix}"
                target = file.with_name(new_name)
                counter += 1

            if new_name != file.name:
                renamed_files.append((file.name, new_name))
                if not dry_run:
                    try:
                        file.rename(target)
                    except Exception as e:
                        print(f"Error renaming {file.name} to {new_name}: {e}")

    return renamed_files


if __name__ == "__main__":
    # Remove "copy_" from all filenames
    renamed = bulk_rename_files(
        directory=r"C:\Personal\Developed\Hailuio\files\gemini",
        pattern=r"\(\d+\)",              # match prefix 'copy_'
        replacement="(1)",                 # remove it
        file_filter="*.txt",            # only txt files
        dry_run=False                   # actually rename
    )

    # for old, new in renamed:
    #     print(f"{old} → {new}")
