import os
import sys
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"}

def get_sort_key(sort_by):
    if sort_by == "created":
        return lambda f: f.stat().st_ctime
    elif sort_by == "modified":
        return lambda f: f.stat().st_mtime
    elif sort_by == "size":
        return lambda f: f.stat().st_size
    elif sort_by == "name":
        return lambda f: f.name.lower()
    else:
        raise ValueError("Invalid sort option")

def create_and_play_pls(folder, sort_by="created", descending=True, auto_play=True):
    folder = Path(folder)

    if not folder.exists():
        print("❌ Folder does not exist")
        return

    video_files = [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
    ]

    if not video_files:
        print("❌ No video files found")
        return

    video_files.sort(
        key=get_sort_key(sort_by),
        reverse=descending
    )

    order = "desc" if descending else "asc"
    pls_path = folder / f"playlist_{sort_by}_{order}.pls"

    # OVERWRITE playlist
    with open(pls_path, "w", encoding="utf-8") as pls:
        pls.write("[playlist]\n")
        for i, video in enumerate(video_files, start=1):
            pls.write(f"File{i}={video.resolve()}\n")
            pls.write(f"Title{i}={video.stem}\n")
            pls.write(f"Length{i}=-1\n")
        pls.write(f"NumberOfEntries={len(video_files)}\n")
        pls.write("Version=2\n")

    print(f"✅ Playlist created: {pls_path}")

    if auto_play:
        os.startfile(pls_path)
        print("▶ Playlist started")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python make_playlist.py <folder> [created|modified|name|size] [asc|desc] [--no-play]")
        sys.exit(1)

    folder_path = sys.argv[1]

    sort_option = "created"
    order = "desc"     # DEFAULT → DESCENDING
    auto_play = True

    for arg in sys.argv[2:]:
        if arg in {"created", "modified", "name", "size"}:
            sort_option = arg
        elif arg in {"asc", "desc"}:
            order = arg
        elif arg == "--no-play":
            auto_play = False

    descending = (order == "desc")

    create_and_play_pls(
        folder_path,
        sort_by=sort_option,
        descending=descending,
        auto_play=auto_play
    )
