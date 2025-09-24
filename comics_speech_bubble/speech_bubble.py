import json
from deepface import DeepFace
from PIL import Image, ImageDraw, ImageFont
import textwrap
from pathlib import Path

# ------------------- helpers -------------------

def load_font(img_w, min_size=16):
    font_size = max(min_size, img_w // 70)
    try:
        return ImageFont.truetype("arial.ttf", font_size)
    except:
        return ImageFont.load_default()

def wrap_text(caption, font, width=25):
    return textwrap.wrap(caption, width=width)

def measure_text(lines, font):
    line_height = font.getbbox("A")[3] + 6
    text_height = line_height * len(lines)
    text_width = max([font.getlength(line) for line in lines])
    return text_width, text_height, line_height

def draw_speech_bubble(draw, face_box, caption, font, img_w):
    top, right, bottom, left = face_box

    lines = wrap_text(caption, font, width=25)
    text_width, text_height, line_height = measure_text(lines, font)

    bubble_w = int(text_width + 40)
    bubble_h = int(text_height + 30)

    bx = left + (right - left)//2 - bubble_w//2
    by = max(10, top - bubble_h - 20)

    draw.ellipse([bx, by, bx + bubble_w, by + bubble_h],
                 fill="white", outline="black", width=3)

    face_center_x = left + (right - left)//2
    tail = [(face_center_x - 10, top),
            (face_center_x + 10, top),
            (face_center_x, top - 20)]
    draw.polygon(tail, fill="white", outline="black")

    for j, line in enumerate(lines):
        text_x = bx + 20
        text_y = by + 15 + j * line_height
        draw.text((text_x, text_y), line, font=font, fill="black")

# ------------------- new helpers -------------------

def load_caption_rules(rules_path):
    with open(rules_path, "r", encoding="utf-8") as f:
        return json.load(f)

def select_caption(age, gender, rules):
    gender_rules = rules.get(gender, {})
    if age < 18:
        return gender_rules.get("<18", "...")
    elif age < 40:
        return gender_rules.get("18-40", "...")
    else:
        return gender_rules.get("40+", "...")

# ------------------- main -------------------

def add_speech_bubbles(image_path, output_path, rules_path="captions.json"):
    rules = load_caption_rules(rules_path)

    analysis = DeepFace.analyze(img_path=image_path, actions=['age', 'gender'], enforce_detection=False)
    pil_img = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(pil_img)
    img_w, _ = pil_img.size
    font = load_font(img_w)

    if not isinstance(analysis, list):
        analysis = [analysis]

    for person in analysis:
        age = person['age']
        gender = person['dominant_gender']
        region = person['region']
        face_box = (region['y'], region['x']+region['w'], region['y']+region['h'], region['x'])

        caption = select_caption(age, gender, rules)
        if "@@" in caption:
            continue
        # caption = "mujhe bas chodna mat baki chahe jo karna"
        draw_speech_bubble(draw, face_box, caption, font, img_w)
        break

    if str(output_path).lower().endswith((".jpg", ".jpeg")):
        pil_img = pil_img.convert("RGB")
    pil_img.save(output_path)
    print(f"✅ Speech bubbles added → {output_path}")


def batch_process(input_dir, output_dir, rules_path="captions.json"):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_files = list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.jpeg")) + list(input_dir.glob("*.png"))
    for img_file in image_files:
        output_file = output_dir / img_file.name
        add_speech_bubbles(img_file, output_file, rules_path)


# add_speech_bubbles("bubble.png", "group_bubbles.png", "captions.json")
batch_process(r"C:\Heaven\Haven\to_cc", r"D:\paradise\stuff\new\captioned_comics", "captions.json")