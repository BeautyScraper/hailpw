from pathlib import Path
from rembg import remove
from PIL import Image
import io
import os

def remove_background(input_path: str, output_path: str = None):
    """
    Removes background from an image, keeping only the main subject (body/object).
    
    Args:
        input_path (str): Path to input image file.
        output_path (str): Path to save output image. 
                           If None, saves with '_nobg.png' suffix.
    """
    # Ensure file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    # Read the image
    with open(input_path, "rb") as inp_file:
        input_data = inp_file.read()
    
    # Remove background
    output_data = remove(input_data)
    
    # Convert to image
    output_image = Image.open(io.BytesIO(output_data))
    
    # Set output filename if not given
    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_nobg.png"

    # Save image (keeps transparency)
    output_image.save(output_path)
    print(f"✅ Background removed and saved to: {output_path}")

# Example usage
from rembg import remove
from PIL import Image
import numpy as np
import os

def crop_body(image_path, output_path=None, padding=30, remove_bg=True, bg_color=(255, 255, 255)):
    """
    Crops the main body/person from an image. 
    
    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the cropped image (optional).
        padding (int): Extra pixels to include around detected body.
        remove_bg (bool): 
            - True  => removes background in final output.
            - False => keeps original background after cropping.
        bg_color (tuple): Background color to use if remove_bg=False and transparent areas appear.
    """
    from rembg import remove  # import inside to avoid startup hang
    
    # Load image
    input_image = Image.open(image_path).convert("RGBA")
    
    # Always remove background temporarily for bounding-box detection
    temp_removed = remove(input_image)
    np_img = np.array(temp_removed)
    alpha = np_img[:, :, 3]
    
    # Find body region
    y_indices, x_indices = np.where(alpha > 0)
    if len(x_indices) == 0 or len(y_indices) == 0:
        print("⚠️ No body detected in:", image_path)
        return None

    # Compute crop box with padding
    x_min = max(0, np.min(x_indices) - padding)
    x_max = min(np_img.shape[1], np.max(x_indices) + padding)
    y_min = max(0, np.min(y_indices) - padding)
    y_max = min(np_img.shape[0], np.max(y_indices) + padding)
    crop_box = (x_min, y_min, x_max, y_max)
    
    # If remove_bg=True → crop the transparent-removed image
    if remove_bg:
        final_img = temp_removed.crop(crop_box)
    else:
        # Crop from original image instead (keep background)
        final_img = input_image.crop(crop_box)
        
        # If any transparency remains, fill with background color
        if final_img.mode == "RGBA":
            bg = Image.new("RGBA", final_img.size, bg_color + (255,))
            bg.paste(final_img, mask=final_img.split()[3])  # merge alpha
            final_img = bg.convert("RGB")
    
    # Determine output path
    base, ext = os.path.splitext(image_path)
    ext = ext.lower()
    if not output_path:
        output_path = f"{base}_body_cropped{ext}"

    # Convert RGBA → RGB for formats that don’t support alpha
    if ext in [".jpg", ".jpeg", ".bmp"]:
        final_img = final_img.convert("RGB")

    final_img.save(output_path)
    print(f"✅ Cropped image saved to: {output_path}")
    return output_path

def batch_dir(image_dir, output_dir, padding=30, remove_bg=True, bg_color=(0, 0, 0)):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for img in os.listdir(image_dir):
        if img.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(image_dir, img)
            print(f"Processing {img_path}...")
            crop_body(img_path, output_path=os.path.join(output_dir, img), padding=padding, remove_bg=remove_bg, bg_color=bg_color)
    
    

# Example usage
if __name__ == "__main__":
    image_dir = r'C:\dumpinGGrounds\rembgpg\files_to_crop'
    output_dir = r'C:\dumpinGGrounds\rembgpg\cropped_output'
    # image_dir = r'C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan3\induced_boy'
    # output_dir = Path(image_dir, image_dir.split(os.sep)[-1] + '_cropped')
    os.makedirs(output_dir, exist_ok=True)
    for img_dir in Path(image_dir).iterdir():
        if img_dir.is_dir():
            batch_dir(str(img_dir), str(Path(output_dir, img_dir.name)), padding=30, remove_bg=False, bg_color=(0, 0, 0))
        
        
    
# if __name__ == "__main__":
#     remove_background("person.jpg")  # Replace with your image path
