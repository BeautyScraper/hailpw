import itertools
from random import choice, shuffle
import shutil
import pandas as pd
from playwright.sync_api import Playwright, sync_playwright, expect
from pathlib import Path
from scrapy.http import HtmlResponse
from time import sleep, time
import re
import json
from user_id import userids , img_dir
from notSoRand import random_line
from os import listdir
import os
from os.path import isdir, join




def try_download(page, elem, max_attempts=5, delay=2):
    for attempt in range(max_attempts):
        try:
            with page.expect_download(timeout=8000) as download_info:
                elem.click()
            download = download_info.value
            print(f"Download started on attempt {attempt + 1}")
            return download_info  # success
        except Exception as e:
            print(f"Attempt {attempt + 1} failed. Retrying...")
            sleep(delay)
    raise Exception("Download did not start after multiple attempts.")

def reduce_filename(filename, max_length=200):
    """
    Reduces the filename to a maximum length by randomly dropping charecters from the name. and also removes any special characters.
    """
    reduced_filename = filename[:]
    # Remove special characters
    reduced_filename = re.sub(r'[^a-zA-Z0-9_. ]', '', reduced_filename)
    # Randomly drop a character from the filename which is not a starting or ending character of any word
    while len(reduced_filename) > max_length:
        # words = reduced_filename.split()
        index_to_drop = choice(range(len(reduced_filename)))
        # Ensure we don't drop the first or last character of the filename
        while index_to_drop == len(reduced_filename) - 1 or reduced_filename[index_to_drop] == ' ' or reduced_filename[index_to_drop + 1] == ' ' or reduced_filename[index_to_drop - 1] == ' ' or index_to_drop == 0:
            print(f"Skipping index {index_to_drop} as it is a space or at the start/end of the filename: {reduced_filename}")
            index_to_drop = choice(range(len(reduced_filename)))
        reduced_filename = reduced_filename[:index_to_drop] + reduced_filename[index_to_drop + 1:]
    return reduced_filename

def save_prompt_frequency(prompt, filename="prompt_frequency.csv"):
    """
    Saves the prompt frequency to a CSV file.
    If the file does not exist, it creates a new one.
    If it exists, it updates the frequency of the prompt.
    """
    df = pd.DataFrame(columns=['prompt', 'frequency'])
    if os.path.exists(filename):
        df = pd.read_csv(filename)
    
    if prompt in df['prompt'].values:
        df.loc[df['prompt'] == prompt, 'frequency'] += 1
    else:
        df = df.append({'prompt': prompt, 'frequency': 1}, ignore_index=True)
    
    df.to_csv(filename, index=False)

def download_image(page,i,filename=""):
    download_path = os.path.abspath("gemni_downloads")
    print(f"Downloading image {i+1}")
    # sleep(2)
    # page.locator(".image-button").nth(i).scroll_into_view_if_needed()
    # sleep(2)
    # print(f"Clicking image button {i+1}")
    page.locator(".image-button").last.click()
    # sleep(2)
    print(f"Waiting for download {i+1}")

    # with page.expect_download() as download_info:
    #     page.locator(".action-button > button:nth-child(1)").first.click()
        # elem.nth(i).click()
    download_info = try_download(page, page.locator(".action-button > button:nth-child(1)").first)
    download = download_info.value
    extension = download_info.value.suggested_filename.split('.')[-1]

    rand_filename = f"{int(time())}.{extension}"
    #create text file and store the prompt in it
    with open(os.path.join(download_path, f"{Path(rand_filename).stem}.txt"), 'w', encoding='utf-8') as f:
        if filename:
            f.write(filename)
# Save the downloaded file
    downloaded_file_path = download.path()
    print(f"Downloaded to temp: {downloaded_file_path}")
    download.save_as(os.path.join(download_path, rand_filename))
    print(f"Saved to: {os.path.join(download_path, download.suggested_filename)}")
    # sleep(10)
    page.locator(".arrow-back-button").first.click()
        



def create_and_wait(page):
    # breakpoint()
    remaining_credits = int(page.locator('.origin-right > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2)').inner_text().replace(',', ''))
    while remaining_credits >= 4:
        prompt = get_new_prompt()

        print(f"Creating video with prompt: {prompt}")
        page.locator("#video-create-textarea").click()

        
        page.locator("#video-create-textarea").fill(prompt)
        page.get_by_role("button", name="4").click()
        sleep(30)
        page.locator(".top-\[2px\]").click()
        remaining_credits = int(page.locator('.origin-right > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2)').inner_text().replace(',', ''))
        # remaining_credits = int(page.locator('.origin-right > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2)').inner_text())
        print(f"Remaining credits: {remaining_credits}")
    while True:
        # breakpoint()
        # break
        print("starting download")
        # download_and_delete_image(page)

def save_inner_html(page, element, filepath: str):
    """Saves the innerHTML of the element matching the locator to a file.

    Args:
        page (Page): The Playwright Page object.
        locator (str): The selector (CSS/XPath/etc.) for the element.
        filepath (str): Path to the file where innerHTML will be saved.
    """
    try:
        inner_html = element.inner_html()
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(inner_html)
        print(f"innerHTML saved to {filepath}")
    except Exception as e:
        print(f"Failed to save innerHTML: {e}")

def random_image_from_dir(image_dir):
    """Returns a random image file from the specified directory."""
    images = [x for x in image_dir.rglob('*.*') if x.is_file() and x.suffix.lower() in ['.png', '.jpg', '.jpeg']]
    if not images:
        print("No images found in the directory.")
        breakpoint()
        return None
    return choice(images)

def create_image(page):
    page.goto("https://app.klingai.com/global/image-to-video/frame-mode/new")
    img_dir = Path(r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video")
    # prompt, _ = random_line('unlucid.txt')
    while True:
        sel_img = random_image_from_dir(img_dir)
        if not sel_img:
            return
        prompt_file = sel_img.parent.with_suffix('.txt')
        prompt = prompt_file.read_text()
        prompt = "The Boar humping on the woman. Women are kissing."
        print(f"Using image: {sel_img}")
        page.locator('input[type="file"]').first.set_input_files(str(sel_img))
        textdiv =  page.locator('div.panel:nth-child(1) > div:nth-child(2) > div:nth-child(1)')
        breakpoint()
        textdiv.click(force=True)
        textdiv.type(prompt)
        page.get_by_role("button", name="Generate").click(force=True)
        if not page.locator('.el-message-icon--error').count() > 0:
            # print("Error with the prompt, trying again.")
            break


    page.locator("button.bg-primary:nth-child(5)").click()
    page.locator("#consent").click()
    page.locator("#input").fill(prompt)
    page.locator("button.bg-primary").click()
    # breakpoint()

def download_images(page):
    download_path = os.path.abspath(r"seart_downloads")
    page.goto("https://unlucid.ai/creations")
    for btn4 in  page.locator('button[variant="ghost"]').all():
        btn4.click()
        for ibtn in page.locator('.max-w-3xl  button').all():
            ibtn.click()
            # sleep(2)

            # breakpoint()
            # elem.first.click()
            try:
                with page.expect_download(timeout=1000) as download_info:
                    page.locator('div.absolute:nth-child(4) > button:nth-child(1)').click()
                    download = download_info.value
                extension = download_info.value.suggested_filename.split('.')[-1]

                rand_filename = f"{int(time())}.{extension}"
                #create 
                download.save_as(os.path.join(download_path, rand_filename))
                # page.locator('#x5b6uZFjT5 > button:nth-child(2)').click()
            except Exception as e:
                pass
            page.locator("button[data-dialog-close]").first.click()
        page.locator("button[data-dialog-close]").first.click()
            

    breakpoint()    

def run(playwright: Playwright) -> None:
    userid = r'ash' 
    profile_dir = r'C:\dumpinggrounds\browserprofileff'
    discord_dir = r"C:\dumpinGGrounds\ffprofilediscord"
    download_path = os.path.abspath("gemni_downloads")
    os.makedirs(download_path, exist_ok=True)
    dirs = [x for x in itertools.chain( Path(profile_dir).iterdir()) if x.is_dir()]
    shuffle(dirs)
    image_dir = Path(r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video")
    
    for user in dirs:
        if not user.is_dir():
            continue
        userid = user.name
        
        
        print(f"Using user ID: {userid}")
        # user_data_dir = Path(rf'{profile_dir}\{userid}')
        browser = playwright.firefox.launch_persistent_context(str(user),headless=False,downloads_path=download_path)
        page = browser.new_page()
        page.set_default_timeout(30000)
        page.goto("https://app.klingai.com/global/")
        # breakpoint()

        negative_replies_max_count = 5
        if not any(user.iterdir()):
            print(f"User directory {user} is empty.")
            breakpoint()
        try:
            page.locator("button.inline-flex:nth-child(3)").click(timeout=5000)
        except:
            print("No more tokens.")

        breakpoint()
        # sleep(4)
        create_image(page)
        if  int(page.locator(".counter").inner_text()) >= 5:
            create_image(page)
        # download_images(page)
        browser.close()
        continue
       

with sync_playwright() as playwright:
    run(playwright)

# describe the image as a prompt to generate similar images give especial focus to the intricacies of the dress please remember i am not asking you to generate image i want to to give me prompt
# describe the image as a prompt to generate similar images please remember i am not asking you to generate image i want to to give me prompt