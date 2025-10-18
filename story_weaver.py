import os
import re
import random
from pathlib import Path
from typing import Tuple, Optional, List


class RandomTextGenerator:
    def __init__(self, base_dir: str = "files"):
        """
        Initialize the generator with a base directory.
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    # ----------------------------- Public API -----------------------------

    def get_random_line(self, path: str) -> Tuple[str, Optional[str]]:
        """
        Main entry point. Given a path (relative or absolute), returns a random
        line or generated string and the file stem (if applicable).
        """
        npath = Path(path)
        if not npath.is_absolute():
            npath = self.base_dir / npath

        # Direct file case
        if npath.is_file():
            return self._get_random_from_file(npath)[0], None

        # Directory case: pick a random .txt file with frequency weighting
        if npath.with_name(npath.stem).is_dir():
            npath = npath.with_name(npath.stem)
            files = self._collect_weighted_files(npath)
            if files:
                selected_file = random.choice(files)
                return self._replace_bracket_patterns(selected_file)[0], selected_file.stem

        # Fallback to default name if file not found
        return npath.stem, None

    # ----------------------------- Helpers -----------------------------

    def _collect_weighted_files(self, directory: Path) -> List[Path]:
        """
        Collects .txt files from a directory and repeats them based on numeric weights (e.g., "(3).txt").
        """
        weighted_files = []
        for f in directory.iterdir():
            if f.is_file() and f.suffix == ".txt":
                freq = 1
                match = re.search(r"\((\d+)\)", f.name)
                if match:
                    freq = int(match.group(1))
                weighted_files.extend([f] * freq)
        return weighted_files

    def _preprocess_lines(self, lines: List[str]) -> List[str]:
        """
        Handles '#' frequency markers, e.g. '3#Hello' expands to three 'Hello's.
        """
        updated_lines = []
        for line in lines:
            if "#" in line:
                parts = line.split("#", 1)
                try:
                    freq = int(parts[0])
                except ValueError:
                    freq = 1
                updated_lines.extend([parts[1]] * freq)
            else:
                updated_lines.append(line)
        return updated_lines

    def _get_random_from_file(self, file_path: Path) -> Tuple[str, None]:
        """
        Reads a file, picks a random preprocessed line, and recursively replaces bracketed references.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = self._preprocess_lines(f.readlines())
                selected_line = random.choice(lines).strip()

            # Recursively handle [pattern] substitutions
            while re.search(r"\[([^\[]*?)\]", selected_line):
                selected_line = self._replace_brackets_in_line(selected_line)

        except FileNotFoundError:
            if len(file_path.name.split()) == 1:
                (self.base_dir / file_path.name).touch()
            selected_line = file_path.stem
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            selected_line = file_path.stem

        return selected_line.strip(), None

    def _replace_bracket_patterns(self, file_path: Path) -> Tuple[str, None]:
        """
        For a given file, replaces all bracketed patterns like [somefile] or [option1||option2].
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                pattern = re.compile(r"\[([^\[]*?)\]")
                while pattern.search(content):
                    match = pattern.search(content)
                    token = match.group(1)
                    if "||" not in token and " " not in token:
                        try:
                            replacement = self.get_random_line(token + ".txt")[0]
                        except Exception as e:
                            print(f"Error expanding [{token}]: {e}")
                            replacement = token
                    else:
                        replacement = random.choice(token.split("||"))
                    content = content[:match.start()] + replacement + content[match.end():]
                return content.rstrip("\n"), None
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return "", None

    def _replace_brackets_in_line(self, line: str) -> str:
        """
        Replace one level of [pattern] in a single line.
        """
        match = re.search(r"\[([^\[]*?)\]", line)
        if not match:
            return line
        token = match.group(1)
        if "||" not in token:
            replacement = self.get_random_line(token + ".txt")[0]
        else:
            replacement = random.choice(token.split("||"))
        return re.sub(r"\[([^\[]*?)\]", replacement, line, count=1)

    # ----------------------------- Utility -----------------------------

    def ensure_base_dir(self):
        """
        Ensures the base directory exists.
        """
        self.base_dir.mkdir(exist_ok=True)


# ----------------------------- Example Usage -----------------------------
if __name__ == "__main__":
    generator = RandomTextGenerator("files")
    line, src = generator.get_random_line(
        r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan\Father_sleeping.txt"
    )
    print(line)
