

from pathlib import Path
from random import choice
from notSoRandV2 import random_line


def random_image_from_dir(image_dir):
    """Returns a random image file from the specified directory."""
    images = [x for x in image_dir.rglob('*.*') if x.is_file() and x.suffix.lower() in ['.png', '.jpg', '.jpeg'] and '6969' not in str(x)]
    if not images:
        print("No images found in the directory.")
        breakpoint()
        return None
    return choice(images)

def get_random_image_and_prompt(dir):
    image_dir = Path(dir)
    sel_img = random_image_from_dir(image_dir)
    prompt_file = sel_img.parent.with_suffix('.txt')
    if sel_img.with_suffix('.txt').exists():
        prompt_file = sel_img.with_suffix('.txt')
    # prompt = prompt_file.read_text()
    prompt = random_line(prompt_file)[0]
    neg_prompt_file = image_dir / 'negative_prompts.neg.txt'
    if '6969' in str(sel_img).lower():
        print("Image is marked as don't use, skipping.")
        return get_random_image_and_prompt(dir)
    if neg_prompt_file.exists():
        neg_prompts = [line.strip() for line in neg_prompt_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        if prompt in neg_prompts:
            print("Prompt is present in negative prompts.")
            return get_random_image_and_prompt(dir)
    return sel_img, prompt


def save_all_req_resp(page,filename):
    respinse_save_dir = Path(r"C:\dumpinGGrounds\reqresp") 
    respinse_save_dir.mkdir(parents=True, exist_ok=True)
    filename = respinse_save_dir / filename
    def handle_request(request):
        with open(filename, "a+", encoding="utf-8") as f:
            f.write(f"REQUEST: {request.method} {request.url}\nHeaders: {request.headers}\n\n")

    def handle_response(response):
        with open(filename, "a+", encoding="utf-8") as f:
            f.write(f"RESPONSE: {response.status} {response.url}\nHeaders: {response.headers}\n\n")

    page.on("request", handle_request)
    page.on("response", handle_response)

def replace_a_line_in_file(file_path, target_line, new_line):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    with open(file_path, "w", encoding="utf-8") as file:
        for line in lines:
            if line.strip() == target_line:
                file.write(new_line + "\n")
            else:
                file.write(line)

def read_lines_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        linesr = []
        for line in lines:
            linestemp = [random_line(line)[0] for _ in range(2000)]
            linestemp = list(set(linestemp))
            linesr.extend(linestemp)
    return lines

def build_origin_map(neg_lines, txt_files):
    """Build a map from negative prompt lines to their origin .txt filenames."""
    origin_map = {}
    for txt_file in txt_files:
        try:
            lines = read_lines_from_file(txt_file)
        except Exception:
            continue
        for line in lines:
            if line in neg_lines:
                origin_map.setdefault(line, []).append(txt_file.name)
    return origin_map

def annotate_lines_with_origins(neg_lines, origin_map):
    """Append '@@filename' to each negative prompt line if an origin is found."""
    new_lines = []
    for line in neg_lines:
        origins = origin_map.get(line, [])
        if origins:
            new_lines.append(f"{line} @@{'|'.join(origins)}")
        else:
            new_lines.append(line)
    return new_lines

def annotate_negative_prompts_with_origin(neg_file_path, search_dir):
    """
    For each line X in negative_prompts.neg.txt, finds the .txt file in search_dir
    such that random_line(file) returns X, and appends '@@filename' after X in neg_file_path.
    """
    neg_file = Path(neg_file_path)
    search_dir = Path(search_dir)
    if not neg_file.exists():
        print(f"{neg_file} does not exist.")
        return

    neg_lines = read_lines_from_file(neg_file)
    txt_files = list(search_dir.rglob("*.txt"))
    txt_files = [f for f in txt_files if f != neg_file]
    origin_map = build_origin_map(neg_lines, txt_files)
    new_lines = annotate_lines_with_origins(neg_lines, origin_map)
    neg_file.write_text('\n'.join(new_lines), encoding="utf-8")

if __name__ == '__main__':
    # img_dir = r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan"
    # sel_img, prompt = get_random_image_and_prompt(img_dir)
    # print(sel_img)
    # print(prompt)
    annotate_negative_prompts_with_origin(r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan\negative_prompts.neg.txt", r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan")