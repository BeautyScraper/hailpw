import os
import re
import random
from pathlib import Path
from typing import Tuple, Optional, List


class RandomTextGenerator:
    """
    A flexible text generation system that:
      • Expands patterns like [reference] and [option1||option2]
      • Handles @section@ definitions inside the same file
      • Supports weighted files and line repetition
    """

    def __init__(self, base_dir: str = "files"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    # ----------------------------- Public API -----------------------------

    def get_random_line(self, path: str) -> Tuple[str, Optional[str]]:
        """
        Given a path (relative or absolute), returns a random expanded line
        and optionally the file stem.
        """
        npath = Path(path)
        if not npath.is_absolute():
            npath = self.base_dir / npath

        # If it's a file directly
        if npath.is_file():
            return self._get_random_from_file(npath)[0], None

        # If a directory exists matching the name
        if npath.with_name(npath.stem).is_dir():
            npath = npath.with_name(npath.stem)
            files = self._collect_weighted_files(npath)
            if files:
                selected_file = random.choice(files)
                return self._replace_bracket_patterns(selected_file)[0], selected_file.stem

        # Fallback
        return npath.stem, None

    # ----------------------------- Internal Helpers -----------------------------

    def _collect_weighted_files(self, directory: Path) -> List[Path]:
        """Collects .txt files from a directory and repeats them by weight."""
        weighted_files = []
        for f in directory.iterdir():
            if f.is_file() and f.suffix == ".txt":
                freq = 1
                match = re.search(r"\((\d+)\)", f.name)
                if match:
                    freq = int(match.group(1))
                weighted_files.extend([f] * freq)
        return weighted_files

    def _preprocess_at(self,file_path,selected_line):
        sl = selected_line
        at_string = re.search('@[^@]+@', sl)
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        while at_string:
            replacement = random.choice([x.strip().split(':')[-1].strip('@') for x in lines if re.match(at_string.group(0)[:-1],x)])
            sl = re.sub('@[^@]+@', replacement, sl, count=1)
            # breakpoint()
            at_string = re.search('@[^@]+@', sl)
        return sl


    def _preprocess_lines(self, lines: List[str]) -> List[str]:
        """Expands frequency markers like '3#Hello'."""
        updated_lines = []
        for line in lines:
            if re.match('@',line):
                continue
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
        """Reads a file and returns a random processed line."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = self._preprocess_lines(f.readlines())
                selected_line = random.choice(lines).strip()
            if '@' in selected_line:
                selected_line = self._preprocess_at(file_path,selected_line)
            # Expand inline and bracket patterns
            selected_line = self._expand_inline_and_brackets(selected_line, file_path)

        except FileNotFoundError:
            if len(file_path.name.split()) == 1:
                (self.base_dir / file_path.name).touch()
            selected_line = file_path.stem
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            selected_line = file_path.stem

        return selected_line.strip(), None

    # ----------------------------- Pattern Expansion -----------------------------

    def _extract_inline_sections(self, content: str) -> Tuple[str, dict]:
        """
        Extracts inline @sections@ from content.

        Example:
          @kehiye@
          hello
          hi

        Returns:
          (content_without_sections, {'kehiye': ['hello', 'hi']})
        """
        sections = {}
        lines = content.splitlines()
        cleaned_lines = []
        current_key = None
        current_lines = []

        for line in lines:
            line = line.rstrip("\n")

            # Start of a section
            if re.fullmatch(r"@\w+@", line.strip()):
                # Save previous section if any
                if current_key and current_lines:
                    sections[current_key] = current_lines
                    current_lines = []
                current_key = line.strip("@").strip()
                continue

            # Inside section
            if current_key:
                if line.strip() == "":
                    # Blank line ends section
                    if current_lines:
                        sections[current_key] = current_lines
                        current_key = None
                        current_lines = []
                    continue
                else:
                    current_lines.append(line.strip())
                    continue

            # Normal content line
            cleaned_lines.append(line)

        # Save final section if needed
        if current_key and current_lines:
            sections[current_key] = current_lines

        return "\n".join(cleaned_lines), sections

    def _replace_bracket_patterns(self, file_path: Path) -> Tuple[str, None]:
        """
        Handles:
          • [reference] → replaced using another file
          • [option1||option2] → random choice
          • @section@ → replaced from inline definitions
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                raw_content = file.read()

                # Extract inline @sections@
                content, sections = self._extract_inline_sections(raw_content)

                # Handle [something] patterns
                bracket_pattern = re.compile(r"\[([^\[]*?)\]")
                while bracket_pattern.search(content):
                    match = bracket_pattern.search(content)
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

                # Replace inline @sections@
                content = self._replace_inline_at_patterns(content, sections)
                return content.rstrip("\n"), None

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return "", None

    def _replace_inline_at_patterns(self, content: str, sections: dict) -> str:
        """Replaces @section@ with a random line from that section."""
        pattern = re.compile(r"@(\w+)@")

        while pattern.search(content):
            match = pattern.search(content)
            key = match.group(1)
            if key in sections and sections[key]:
                replacement = random.choice(sections[key])
            else:
                replacement = f"@{key}@"
            content = content[:match.start()] + replacement + content[match.end():]
        return content

    def _expand_inline_and_brackets(self, line: str, file_path: Path) -> str:
        """Handles inline [pattern] and @section@ replacements inside single lines."""
        # Replace [pattern]
        while re.search(r"\[([^\[]*?)\]", line):
            match = re.search(r"\[([^\[]*?)\]", line)
            token = match.group(1)
            if "||" not in token:
                replacement = self.get_random_line(token + ".txt")[0]
            else:
                replacement = random.choice(token.split("||"))
            line = re.sub(r"\[([^\[]*?)\]", replacement, line, count=1)

        # Handle @section@ from inline definitions if file contains them
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
            _, sections = self._extract_inline_sections(raw_content)
            line = self._replace_inline_at_patterns(line, sections)
        except Exception:
            pass

        return line


# ----------------------------- Example Usage -----------------------------

if __name__ == "__main__":
    generator = RandomTextGenerator("files")
    line, src = generator.get_random_line(
        r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan3\cuck_son\start.txt"
    )
    print(line)
