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
from notSoRand import randomLine
from os import listdir
import os
from os.path import isdir, join

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def get_new_prompt():
    # This function should return a new prompt for the video creation
    # For now, we will return a static prompt
    prompt = randomLine('gemni.txt')
    # prompt = "Generate 16:9 image: A voluptuous woman revealing her midriff with South Asian features, adorned in elaborate gold jewelry including a detailed necklace, bracelets, and headpiece with sun-like elements, is seated on an ornate golden chariot-like throne. She wears a heavily embellished, revealing gold costume made with chains that appears to be part of a traditional or fantasy setting. The backdrop features a partly cloudy sky. The overall style should evoke a sense of ancient royalty or a powerful mythological figure "
    
    return prompt

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
    print(Colors.GREEN + f"Downloading image {i+1}"  )
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
    print(f"Saved to: {os.path.join(download_path, download.suggested_filename)}"+ Colors.RESET)
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


def run(playwright: Playwright) -> None:
    userid = r'ash' 
    profile_dir = r'C:\dumpinggrounds\browserprofileff'
    download_path = os.path.abspath("gemni_downloads")
    os.makedirs(download_path, exist_ok=True)
    dirs = [x for x in Path(profile_dir).iterdir() if x.is_dir()]
    shuffle(dirs)
    
    for user in dirs:
        if not user.is_dir():
            continue
        userid = user.name
        if "chilli" in userid:
            continue
        print(f"Using user ID: {userid}")
        user_data_dir = Path(rf'{profile_dir}\{userid}')
        browser = playwright.firefox.launch_persistent_context(user_data_dir,headless=True,downloads_path=download_path)
        page = browser.new_page()
        # breakpoint()
        page.set_default_timeout(60000 * 2)
        page.goto("https://gemini.google.com")

        negative_replies_max_count = 5
        for i in range(100):
            # breakpoint()
            # if "sense" in userid:
            #     breakpoint()
            #     pass
            # else:
            #     print(f"Skipping user {userid} as it is not an image generation user")
            #     break
            try:
                prompt = get_new_prompt()
                print(Colors.BLUE + f"Creating image with prompt: {prompt}" + Colors.RESET)
                print(Colors.YELLOW + f"Iteration {i+1}, User ID: {userid}, Negative Replies Max Count: {negative_replies_max_count}" + Colors.RESET)
                page.locator(".ql-editor").click()
                sleep(1)
                page.locator(".ql-editor").fill(prompt)
                sleep(1)
                page.locator(".send-button").scroll_into_view_if_needed()
                sleep(1)
                total_text_replys = len(page.locator("[id*=model-response-message-contentr_]").all()) + 1 - 1
                sleep(1)
                # save_inner_html(page, page.locator(".send-button"), f"ss\\{userid}_send_button_before.html")
                # breakpoint()
                if not  "hidden" in page.locator(".send-button").locator('[fonticon="send"]').first.get_attribute("class"):
                    page.locator(".send-button").click()
                else:
                    page.screenshot(path=f"ss\\{userid}_send_button_hidden.png")
                # save_inner_html(page, page.locator(".send-button", f"ss\\{userid}_send_button_after.html"))
                
                # breakpoint()
                # negative_replies = ["cannot generate an image","sexually suggestive","can't fulfill that request","find one on the web","pictures for you online","cannot fulfill","still learning how to generate certain kinds of images, so I might not be able","unable to generate an image",  "sexually explicit", "against my guidelines"]
                with open("negative_replies.txt", "r") as f:
                    negative_replies = [x.strip() for x in f.read().splitlines()]
                
                user_changing_replies = ["generate more images for you today", "create more images for you today","I am sorry, but I am unable to generate images for you today", "I am unable to generate images for you today", "I am unable to create images for you today", "I am unable to create images for you today"]
                sleep(5)
                reply = page.locator("[id*=model-response-message-contentr_]").last.text_content()
                retry_count = 50
                total_img_replys = len(page.locator(".image-button").all())
                #message-content-id-r_b66701772c70dc9f
                img_new_reply_count = 0
                txt_new_reply_count = 0
                image_gen_flag = True
                # while img_new_reply_count <= total_img_replys and retry_count > 0:
                while reply.strip() == "" and len(page.locator(".image-button").all()) <= total_img_replys and retry_count > 0:
                    reply = page.locator("[id*=model-response-message-contentr_]").last.text_content(timeout=5000)
                    sleep(2)
                    # print(f"{total_img_replys} {new_reply_count}",end='.')
                    print(f"",end='.')
                    retry_count -= 1
                if retry_count <= 0:
                    # breakpoint()
                    page.screenshot(path=f"ss\\{userid}_retry_error.png")
                    print("Retry count exceeded, retrying with a different prompt")
                    raise Exception("Retry count exceeded, retrying with a different prompt")
                    continue
                    
                sleep(9)
                print(Colors.CYAN + f"Reply: {reply}" + Colors.RESET)
                # breakpoint()
                for uc in user_changing_replies:
                    if uc in reply:
                        raise Exception("User changing, retrying with a different user")
                for nr in negative_replies:
                    if nr in reply:
                        image_gen_flag = False
                        print(Colors.RED + f"Negative reply detected: {nr}, retrying with a different prompt" + Colors.RESET)
                        break
                if image_gen_flag:
                    negative_replies_max_count += 1
                    save_prompt_frequency(prompt, "pos_prompt_frequency.csv")
                    download_image(page,i,prompt[:])
                else:
                    save_prompt_frequency(prompt)
                    negative_replies_max_count -= 1
                    if negative_replies_max_count < 0:
                        print("Negative replies max count reached, retrying with a different user")
                        raise Exception("Negative replies max count reached, retrying with a different user")
                    print("Image generation failed, retrying with a different prompt")
                    continue
                # sleep(60)
                
            except Exception as e:
                page.screenshot(path=f"ss\\{userid}_error.png")
                print(f"An error occurred: {e}")
                print("An error occurred, retrying...with different user\n\n\n\n\n\n\n")
                break
        # breakpoint()
        # elems = page.locator("generated-image:nth-child(1) > single-image:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > download-generated-image-button:nth-child(1) > button:nth-child(1)").all()
        browser.close()
        continue
        for i,elem in enumerate(elems):
            print(f"Downloading image {i+1}/{len(elems)}")
            page.locator(".image-button").nth(i).scroll_into_view_if_needed()
            page.locator(".image-button").nth(i).click()
            with page.expect_download() as download_info:
                page.locator(".action-button > button:nth-child(1)").first.click()
                # elem.nth(i).click()
            
            download = download_info.value
            extension = download_info.value.suggested_filename.split('.')[-1]
            rand_filename = f"{int(time())}.{extension}"
    # Save the downloaded file
            downloaded_file_path = download.path()
            print(f"Downloaded to temp: {downloaded_file_path}")
            download.save_as(os.path.join(download_path, rand_filename))
            print(f"Saved to: {os.path.join(download_path, download.suggested_filename)}")
            page.locator(".arrow-back-button").first.click()
            # page.locator("generated-image:nth-child(1) > single-image:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > download-generated-image-button:nth-child(1) > button:nth-child(1)").first.click()

        # breakpoint()
        # page.locator("div").filter(has_text=re.compile(r"^VideoImage$")).get_by_role("img").nth(1).click()
        
        # # page.get_by_text("Image-0116:9").click()

        # page.locator("div").filter(has_text=re.compile(r"^Image-0116:9$")).locator("span").nth(2).click()
        # page.get_by_text("9:16").last.click()
        # try:
        #     create_and_wait(page)
        # except Exception as e:
        #     print(f"Error during creation: {e}")
        #     # Optionally, you can log the error or take a screenshot
        #     page.screenshot(path=f"{userid}_error.png")
        #     continue
        # page.wait_for_timeout(10000)
        
        browser.close()

with sync_playwright() as playwright:
    run(playwright)

# describe the image as a prompt to generate similar images give especial focus to the intricacies of the dress please remember i am not asking you to generate image i want to to give me prompt
# describe the image as a prompt to generate similar images please remember i am not asking you to generate image i want to to give me prompt