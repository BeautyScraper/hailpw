import shutil
from pathlib import Path
import glob


def copy_by_patterns(scan_dir: str, source_dir: str) -> None:
    """
    Scan subdirectories of scan_dir for move.txt files.
    For each move.txt, copy files from source_dir matching wildcard patterns
    into that subdirectory, while preventing duplicate copies using copydb.txt.
    """

    scan_dir = Path(scan_dir)
    source_dir = Path(source_dir)

    if not scan_dir.is_dir():
        raise ValueError(f"scan_dir does not exist or is not a directory: {scan_dir}")

    if not source_dir.is_dir():
        raise ValueError(f"source_dir does not exist or is not a directory: {source_dir}")

    for subdir in scan_dir.iterdir():
        if not subdir.is_dir():
            continue

        move_file = subdir / "move.txt"
        if not move_file.exists():
            continue

        print(f"\nProcessing directory: {subdir}")

        # Read patterns
        patterns = [
            line.strip()
            for line in move_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        if not patterns:
            print("  move.txt is empty, skipping.")
            continue

        copydb_path = subdir / "copydb.txt"

        # Load already copied files
        if copydb_path.exists():
            copied_files = set(
                line.strip()
                for line in copydb_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        else:
            copied_files = set()

        newly_copied = []

        for pattern in patterns:
            search_pattern = str(source_dir / pattern)
            matches = glob.glob(search_pattern)

            for file_path in matches:
                src = Path(file_path)

                if not src.is_file():
                    continue

                # Use filename as copy key (simple & portable)
                file_key = src.name

                if file_key in copied_files:
                    print(f"  Skipped (already copied): {file_key}")
                    continue

                dest = subdir / src.name

                shutil.copy2(src, dest)
                copied_files.add(file_key)
                newly_copied.append(file_key)

                print(f"  Copied: {file_key}")

        # Update copydb.txt
        if newly_copied:
            with copydb_path.open("a", encoding="utf-8") as db:
                for fname in newly_copied:
                    db.write(fname + "\n")

        print(f"  Completed: {len(newly_copied)} new files copied.")

if __name__ == "__main__":
    copy_by_patterns(
    scan_dir=r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan3",
    source_dir=r"C:\Personal\Developed\Hailuio\gemni_downloads"
)
    copy_by_patterns(
    scan_dir=r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\queue_wan",
    source_dir=r"C:\Personal\Developed\Hailuio\gemni_downloads"
)

