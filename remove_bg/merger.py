import os
from pathlib import Path
import random
from PIL import Image

def merge_random_images(directory, out_dir, vertical=True):
    # Valid image extensions
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")

    # Get all images in directory
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(valid_extensions)]

    # Ensure at least 2 images exist
    if len(image_files) < 2:
        print(f"Not enough images in directory: {directory}")
        return

    # Pick two random images
    img1_name, img2_name = random.sample(image_files, 2)
    img1_path = os.path.join(directory, img1_name)
    img2_path = os.path.join(directory, img2_name)

    # Open images
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)

    # Merge vertically
    if vertical:
        # Resize second image to match width
        img2 = img2.resize((img1.width, img2.height * img1.width // img2.width))
        total_height = img1.height + img2.height
        merged_img = Image.new("RGB", (img1.width, total_height))
        merged_img.paste(img1, (0, 0))
        merged_img.paste(img2, (0, img1.height))
    else:
        # Merge horizontally
        img2 = img2.resize((img2.width * img1.height // img2.height, img1.height))
        total_width = img1.width + img2.width
        merged_img = Image.new("RGB", (total_width, img1.height))
        merged_img.paste(img1, (0, 0))
        merged_img.paste(img2, (img1.width, 0))

    # Generate output filename from input names (without extensions)
    base1 = os.path.splitext(img1_name)[0]
    base2 = os.path.splitext(img2_name)[0]
    output_name = f"{base1}_{base2}_merged.jpg"
    output_path = os.path.join(out_dir, output_name)

    # Save merged image
    merged_img.save(output_path)
    print(f"Merged image saved as: {output_path}")


def merge_random_images_from_subdirs(parent_dir, out_dir, vertical=True):
    """
    Randomly picks two images from different subdirectories under parent_dir
    and merges them using the same logic as merge_random_images.
    """
    # Get subdirectories
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    subdirs = [os.path.join(parent_dir, d) for d in os.listdir(parent_dir)
               if os.path.isdir(os.path.join(parent_dir, d))]

    if len(subdirs) < 2:
        print("Not enough subdirectories to choose from!")
        return

    # Pick two random subdirectories
    dir1, dir2 = random.sample(subdirs, 2)

    # Get image files in each subdir
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    imgs_dir1 = [f for f in os.listdir(dir1) if f.lower().endswith(valid_extensions)]
    imgs_dir2 = [f for f in os.listdir(dir2) if f.lower().endswith(valid_extensions)]

    if not imgs_dir1 or not imgs_dir2:
        print("One or both subdirectories have no valid images.")
        return

    # Pick one random image from each directory
    img1_name = random.choice(imgs_dir1)
    img2_name = random.choice(imgs_dir2)

    img1_path = os.path.join(dir1, img1_name)
    img2_path = os.path.join(dir2, img2_name)

    # Open and merge the selected images
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)

    if vertical:
        img2 = img2.resize((img1.width, img2.height * img1.width // img2.width))
        total_height = img1.height + img2.height
        merged_img = Image.new("RGB", (img1.width, total_height))
        merged_img.paste(img1, (0, 0))
        merged_img.paste(img2, (0, img1.height))
    else:
        img2 = img2.resize((img2.width * img1.height // img2.height, img1.height))
        total_width = img1.width + img2.width
        merged_img = Image.new("RGB", (total_width, img1.height))
        merged_img.paste(img1, (0, 0))
        merged_img.paste(img2, (img1.width, 0))

    # Output name combines both filenames and subdir names
    base1 = os.path.splitext(img1_name)[0]
    base2 = os.path.splitext(img2_name)[0]
    dir1_name = os.path.basename(dir1)
    dir2_name = os.path.basename(dir2)

    output_name = f"{dir1_name}_{base1}__{dir2_name}_{base2}_merged.jpg"
    output_path = os.path.join(out_dir, output_name)

    merged_img.save(output_path)
    print(f"Merged image from different folders saved as: {output_path}")


# Example usage:
for i in range(50):
    merge_random_images_from_subdirs(
        r"C:\dumpinGGrounds\rembgpg\cropped_output",
        r"C:\dumpinGGrounds\rembgpg\merged_op",
        vertical=False
    )
