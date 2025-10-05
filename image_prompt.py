

import itertools
from pathlib import Path
import queue
from random import choice
from notSoRandV2 import random_line
import threading
import re
import time
import pandas as pd
import subprocess
import sys

csv_file =  Path(r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan\genvideo_details.csv") #the csv file has these column user	sel_image	prompt	nsfw	success	httpCode	errorCode	data	requestId	failed	traceId

def run_command_with_timeout(cmd, timeout):
    """
    Runs a command and displays output in real-time.
    Kills the process if it exceeds the timeout.
    Timeout is in seconds (can be fractional).
    """
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=isinstance(cmd, str)  # True if cmd is a string
        )

        q = queue.Queue()

        def enqueue_output(out, queue):
            for line in iter(out.readline, ''):
                queue.put(line)
            out.close()

        t = threading.Thread(target=enqueue_output, args=(process.stdout, q))
        t.daemon = True
        t.start()

        start = time.time()
        timed_out = False

        while True:
            try:
                line = q.get_nowait()
            except queue.Empty:
                pass
            else:
                print(line, end="")  # Print real-time output

            if process.poll() is not None:  # process finished
                break

            if time.time() - start > timeout:  # timeout check
                timed_out = True
                process.terminate()
                try:
                    process.wait(2)
                except subprocess.TimeoutExpired:
                    process.kill()
                print("\nProcess killed after timeout")
                break

            time.sleep(0.1)  # prevent busy loop

        return process.returncode, timed_out

    except Exception as e:
        print("Error:", e)
        return -1, True

def save_response_to_csv(response, name, sel_img, prompt):
    """
    Saves the response data along with user information, selected image, and prompt to a CSV file.

    Parameters:
        response: The response object with a .json() method containing additional data.
        name (str): The name of the user.
        sel_img (str or Path): The path to the selected image.
        prompt (str): The prompt associated with the image.

    The function creates or appends to 'genvideo_details.csv' in the image's parent directory.
    """
    # csv_file = Path(csv_file)
    data = {
        "user": name,
        "sel_image": str(sel_img),
        "prompt": prompt,
        "nsfw": "NA",
        **response.json()
    }
    df = pd.DataFrame([data])
    if csv_file.exists():
        df.to_csv(csv_file, mode='a', header=False, index=False, encoding="utf-8")
    else:
        df.to_csv(csv_file, mode='w', header=True, index=False, encoding="utf-8")

def get_info_by_data_column( data):
    """
    Fetches rows from the CSV file where the 'data' column matches the given value.

    Parameters:
        data: The value to match in the 'data' column.

    Returns:
        pandas.DataFrame: DataFrame containing matching rows, or empty DataFrame if none found.
    """
    df = pd.read_csv(csv_file, encoding="utf-8")
    if 'data' not in df.columns:
        print("'data' column not found in CSV.")
        return pd.DataFrame()
    return df[df['data'] == data]

def update_nsfw(data, is_nsfw):
    """
    Updates the 'nsfw' column for rows where the 'data' column matches the given value.

    Parameters:
        data: The value to match in the 'data' column.
        is_nsfw: The value to set in the 'nsfw' column.
    """
    df = pd.read_csv(csv_file, encoding="utf-8")
    if 'data' not in df.columns or 'nsfw' not in df.columns:
        print("Required columns not found in CSV.")
        return
    df.loc[df['data'] == data, 'nsfw'] = is_nsfw
    df.to_csv(csv_file, index=False, encoding="utf-8")

def notify_sleep(seconds):
    for i in range(1, seconds + 1, 5):
        time.sleep(5)
        print(f"\r{int(i/seconds*100)}%", end="", flush=True)
    print("Done waiting!")

def input_with_timeout(prompt, timeout, default):
    user_input = [default]  # use list so inner function can modify it

    def get_input():
        user_input[0] = input(prompt) or default

    t = threading.Thread(target=get_input)
    t.daemon = True
    t.start()
    t.join(timeout)

    if t.is_alive():  # time ran out
        print(f"\n⏰ Time’s up! Using default: {default}")
        return default
    return user_input[0]

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
    if '6969' in str(sel_img).lower():
        print("Image is marked as don't use, skipping.")
        return get_random_image_and_prompt(dir)
    # breakpoint()
     
    prompt_file = sel_img.with_name(sel_img.parent.with_suffix('.txt').name) 
    if not prompt_file.is_file():
        prompt_file = sel_img.parent / 'start.txt'

    if sel_img.with_suffix('.txt').exists():
        prompt_file = sel_img.with_suffix('.txt')
    if not prompt_file.is_file():
        print(f'{prompt_file} does not exist')
        return get_random_image_and_prompt(dir)
    # prompt = prompt_file.read_text()
    prompt = random_line(prompt_file)[0]
    # if "pyaari" in prompt:
    #     breakpoint()
    neg_prompt_file = image_dir / 'negative_prompts.neg.txt'
    if neg_prompt_file.exists():
        neg_prompts = [line.strip() for line in neg_prompt_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        # breakpoint()
        if prompt in neg_prompts:
            print("Prompt is present in negative prompts.")
            neg_file = sel_img.parent / "negatives.txt"
            with open(neg_file, "a", encoding="utf-8") as f:
                f.write(prompt + "\n")
            return get_random_image_and_prompt(dir)
    else:
        breakpoint()
    return sel_img, prompt

def seperate_sayings(dir):
    dirs = Path(dir)
    for d in dirs.iterdir():
        if not d.is_dir()  or '6969' in str(d):
            continue
        # breakpoint()
        common_prompt_file = d / d.with_suffix('.txt').name
        if not common_prompt_file.is_file():
            continue
        # breakpoint()
        content = common_prompt_file.read_text(encoding="utf-8")
        sections = re.split(r'[,\;\.\n]', content)

        for section in sections:
            quotes = re.findall(r'(.*)["“”](.*?)["“”]', section)[0]
            if quotes and len(quotes) == 2:
                breakpoint()
                fname = quotes[0].strip().replace(' ', '_')
                out_file = d / f"{fname}.txt"
                with open(out_file, "a", encoding="utf-8") as out_f:
                    out_f.write(quotes[1])
                # Replace the quotation in common_prompt_file with [<sub>_<con>]
                # breakpoint()
                new_section = re.sub(r'["“”](.*?)["“”]', f'[{fname}]', section)
                content = content.replace(section, new_section)

        with open(common_prompt_file, "a", encoding="utf-8") as f:
            f.write(content)

        

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

def calculate_nsfw_chances_safe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the probability of each file being NSFW, safely handling zero counts.

    Args:
        df (pd.DataFrame): DataFrame with columns 'sel_image' and 'nsfw'.

    Returns:
        pd.DataFrame: A DataFrame with file, total count, nsfw count, and nsfw probability.
    """
    # Group by file and calculate stats
    result = (
        df.groupby("sel_image")["nsfw"]
        .agg(
            total="count",
            nsfw_count="sum"
        )
        .reset_index()
    )
    # Safely add probability column (avoid division by zero)
    result["nsfw_probability"] = result.apply(
        lambda row: row["nsfw_count"] / row["total"] if row["total"] > 0 else 0, axis=1
    )
    return result

def export_nsfw_reports(df: pd.DataFrame, output_suffix="_nsfw_report.csv"):
    """
    For each sel_image, create a CSV in that file's directory containing 
    prompt-level stats and one extra column with the overall file probability.

    Args:
        df (pd.DataFrame): DataFrame with 'sel_image', 'prompt', and 'nsfw' columns.
        output_suffix (str): Suffix to append for the report file.
    """
    grouped_files = df.groupby("sel_image")
    
    for file, group in grouped_files:
        file_path = Path(file)

        # --- Per-prompt aggregation ---
        prompt_stats = (
            group.groupby("prompt")["nsfw"]
            .agg(total_count="count", nsfw_count="sum")
            .reset_index()
        )

        # Safe division for prompt-level probability
        prompt_stats["nsfw_probability"] = prompt_stats.apply(
            lambda row: row["nsfw_count"] / row["total_count"] if row["total_count"] > 0 else 0,
            axis=1
        )

        # --- Overall probability for this file ---
        total = len(group)
        nsfw_count = group["nsfw"].sum()
        file_nsfw_prob = nsfw_count / total if total > 0 else 0

        # Add as a constant column for all rows
        prompt_stats["overall_file_nsfw_probability"] = file_nsfw_prob

        # --- Output path ---
        file_dir = file_path.parent
        base_name = file_path.stem
        out_path = file_dir / f"{base_name}{output_suffix}"

        # Ensure directory exists
        file_dir.mkdir(parents=True, exist_ok=True)

        # Save CSV
        prompt_stats.to_csv(out_path, index=False)

    print("Reports created successfully.")

if __name__ == '__main__':
    # img_dir = r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan"
    # for i in range(10000):
    #     sel_img, prompt = get_random_image_and_prompt(img_dir)
    #     print(sel_img)
    #     print(prompt)
    # seperate_sayings(img_dir)
    df1 = pd.read_csv(csv_file, encoding="utf-8")
    # nsfw_stats_safe = calculate_nsfw_chances_safe(df1)
    # nsfw_stats_safe.to_csv(csv_file.parent / 'results.csv')
    export_nsfw_reports(df1)
    # breakpoint()
    # annotate_negative_prompts_with_origin(r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan\negative_prompts.neg.txt", r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan")
    # value = input_with_timeout("Enter your name (10s timeout): ", 10, "Guest")
    # print("Final value:", value)