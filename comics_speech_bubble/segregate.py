from pathlib import Path
from random import randint, shuffle
import sys
from deepface import DeepFace
import shutil


sys.path.append(str(Path(r"D:\Developed\comics_creation")))

from notSoRand import random_line
from main import add_comic_narration

def get_new_prompt(filename):
    # This function should return a new prompt for the video creation
    # For now, we will return a static prompt
    # filename = get_relative_name(filename)
    fn = Path('files', filename)
    if not fn.is_file():  # Remove .txt extension
        fn.touch()  # Create an empty file if it doesn't exist
    prompt = random_line(filename)
    return prompt[0]


def sort_images_into_combined_dirs(input_dir, output_dir):
    """
    Sort images into directories based on the combination of persons detected,
    using gender + age as directory name like m32w40m23.

    Parameters:
        input_dir (str | Path): Path to input folder containing images
        output_dir (str | Path): Path to output folder where sorted images will be stored
    """

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    img_paths = []

    for ext in ("*.jpg", "*.jpeg", "*.png"):
        img_paths.extend(input_dir.rglob(ext))

    shuffle(img_paths)
    for img_path in img_paths:
        try:
            # Analyze faces in the image
            analysis = DeepFace.analyze(
                img_path.as_posix(),
                actions=['age', 'gender'],
                detector_backend='retinaface',
                enforce_detection=False
            )

            if not isinstance(analysis, list):
                analysis = [analysis]

            persons = []
            for person in analysis:
                # breakpoint()
                gender = person["dominant_gender"].lower()
                age = int(person["age"])
                if age < 20:
                    age_category = "2"
                elif 20 <= age <= 40:
                    age_category = "4"
                elif 41 <= age <= 60:
                    age_category = "6"
                else:
                    age_category = "8"
                tag = f"{gender[0]}{age_category}"
                
                persons.append(tag)

            # Sort tags for consistency (so m23w40 == w40m23 always goes to the same dir)
            persons.sort()
            file_name = "".join(persons)
            caption = get_new_prompt(Path(file_name).with_suffix('.txt'))
            target_dir = output_dir / f'{img_path.stem}_{file_name}_{randint(1000,9999)}{img_path.suffix}'
            if len(caption) < 20:
                print(f"Caption too short ({len(caption)}): {caption}. Skipping {img_path} filename {file_name}")
                continue
                # caption = random_line(r"D:\Developed\comics_creation\captions.txt")
            add_comic_narration(img_path,target_dir,caption)
            # Create directory
            # target_dir.mkdir(parents=True, exist_ok=True)

            # Copy file
            # dst_file = target_dir / img_path.name
            # shutil.copy(img_path, dst_file)

        except Exception as e:
            print(f"Error processing {img_path}: {e}"+e)


# Example usage:
# sort_images_into_combined_dirs("C:/Users/alind/images", "C:/Users/alind/sorted_images")


# sort_images_into_combined_dirs(r"C:\Heaven\Haven\to_cc", r"D:\paradise\stuff\new\captioned_comics")
# sort_images_into_combined_dirs(r"D:\paradise\stuff\essence\Pictures\Heaps\heap_YummyBaker", r"D:\paradise\stuff\new\captioned_comics")
sort_images_into_combined_dirs(r"D:\paradise\stuff\new\imageset", r"D:\paradise\stuff\new\captioned_comics")