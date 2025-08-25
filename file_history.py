from pathlib import Path
from collections import deque
import hashlib

class FileHistory:
    def __init__(self, max_files=5):
        """Initialize with max number of files to remember."""
        self.max_files = max_files
        self.files = deque(maxlen=max_files)  # stores (path, hash)

    def _file_hash(self, file_path):
        """Compute SHA256 hash of file contents."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def add_file(self, file_path):
        """Add a file and check if it's a duplicate among the last N files."""
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"{file_path} does not exist or is not a file")

        file_hash = self._file_hash(path)

        # Check for duplicate in last N files
        for old_path, old_hash in self.files:
            if file_hash == old_hash:
                return True  # duplicate found

        # Add new file to memory
        self.files.append((path, file_hash))
        return False  # not a duplicate
