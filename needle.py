from pathlib import Path
import shutil
import argparse

def copy_matching_files(search_word: str, src_dir: Path, dst_dir: Path):
    dst_dir.mkdir(parents=True, exist_ok=True)

    # Lowercase search word for case-insensitive matching
    search_word = search_word.lower()

    for txt_file in src_dir.glob("*.txt"):
        mp4_file = txt_file.with_suffix(".mp4")
        png_file = txt_file.with_suffix(".png")
        try:
            content = txt_file.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception as e:
            print(f"⚠️ Could not read {txt_file}: {e}")
            continue

        if search_word in content:
            print(f"✅ Found '{search_word}' in {txt_file.name}, copying...")
            shutil.copy(txt_file, dst_dir)
            if mp4_file.exists():
                shutil.move(mp4_file, dst_dir)
            elif png_file.exists():
                shutil.move(png_file, dst_dir)
            else:
                print(f"⚠️ {mp4_file.name} not found")

def main():
    parser = argparse.ArgumentParser(
        description="Search for a word in .txt files and copy matching .txt + .mp4 files."
    )
    parser.add_argument("word", help="Word to search inside text files (case-insensitive).")  # positional
    parser.add_argument("--src", type=Path, default=Path.cwd(),
                        help="Source directory (default: current working directory).")
    parser.add_argument("--dst", type=Path,
                        help="Destination directory (default: ./<word>).")
    
    args = parser.parse_args()

    # Default destination is ./<word>
    dst_dir = args.dst if args.dst else Path.cwd() / args.word

    copy_matching_files(args.word, args.src, dst_dir)

if __name__ == "__main__":
    main()
