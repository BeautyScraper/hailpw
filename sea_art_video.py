import itertools
from random import choice, randint, shuffle
import shutil
import pandas as pd
from playwright.sync_api import Playwright, sync_playwright, expect
from pathlib import Path
from scrapy.http import HtmlResponse
from time import sleep, time
import re
import json

from tqdm import tqdm
from user_id import userids , img_dir
from notSoRand import random_line
from os import listdir
import os
from os.path import isdir, join
from image_prompt import get_random_image_and_prompt, save_all_req_resp



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

def is_video_processed(video_id, log_file="processed_videos.log"):
    if not os.path.exists(log_file):
        return False
    with open(log_file, 'r') as f:
        processed_ids = f.read().splitlines()
    return video_id in processed_ids
def video_processed(video_id, log_file="processed_videos.log"):
    with open(log_file, 'a') as f:
        f.write(f"{video_id}\n")

def download_videos(page):
    # breakpoint()
    try:
        # page.locator(".model-popover-content-title > i:nth-child(2)").click(timeout=2000)
        page.locator('i[data-event="video_model_recommend_modal_close"]').click(timeout=2000)
    except:
        pass
    # if page.locator(".model-popover-content-title > i:nth-child(2)").click().count() > 0:
    imgboxs = page.locator(".image-render-box").all()
    print(f"Found {len(imgboxs)} videos to process.")
    for i, imgbox in enumerate(reversed(imgboxs)):
        # breakpoint()
        imgbox.scroll_into_view_if_needed()
        # if imgbox.locator("img").count() > 1:
        #     print(f"Skipping video {i+1} as it has many img element.")
            # breakpoint()
            # continue
        if imgbox.locator("img").first.get_attribute('src') is None:
            print(f"Skipping video {i+1} as it has no data-src attribute.")
            continue
        id =  imgbox.locator("img").first.get_attribute('src').split('/')[-1]

         # Check if the video has already been processed
        if is_video_processed(id):
            print(f"Video {id} has already been processed. Skipping...")
            if (randint(1, 100) <= 20):
                break
            continue

        print(f"Processing video {i+1}/{len(imgboxs)}")
        try:
            sleep(1)
            process_imgbox(page, imgbox)
        except Exception as e:
            print(f"Error processing video {i+1}: {e}")
            # breakpoint()
            continue
        # sleep(5)
        video_processed(id)
          # Short delay between processing each video

def process_imgbox(page, imgbox):
    # imgbox = page.locator(".image-render-box").nth(0)
    # id =  imgbox.locator("img").get_attribute('data-src').split('/')[-1]
    imgbox.hover()
    page.locator(".el-icon-more.el-popover__reference").nth(0).hover()
    elem = imgbox.locator('[data-id="download"]')
    if elem.count() > 0:
        download_path = os.path.abspath(r"seart_downloads")
        elem.first.click()
        with page.expect_download(timeout=16000) as download_info:
            download = download_info.value
        extension = download_info.value.suggested_filename.split('.')[-1]

        rand_filename = f"{int(time())}.{extension}"
        #create 
        if extension.lower() in ['mp4', 'mov', 'avi', 'mkv']:
            # breakpoint()
            download_path = os.path.abspath(r"seart_downloads\mp4s")
        download.save_as(os.path.join(download_path, rand_filename))
    


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
    sleep(20)
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
def replace_a_line_in_file(file_path, target_line, new_line):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    with open(file_path, "w", encoding="utf-8") as file:
        for line in lines:
            if line.strip() == target_line:
                file.write(new_line + "\n")
            else:
                file.write(line)

def generate_images(page):
    with open("seaart_models.txt", "r", encoding="utf-8") as f:
        urls = [line.strip().split("@@")[0] for line in f if line.strip() and '##' not in line]
    if not urls:
        print("No URLs found in seaart_models.txt")
        return
    selected_url = choice(urls)
    print(f"Randomly selected model URL: {selected_url}")
    page.goto(selected_url)
    replace_a_line_in_file("seaart_models.txt", selected_url, f"{selected_url}@@{ page.title()}")
    # breakpoint()
    page.locator("div.btns-container-item:nth-child(1)").click()
    # color = choice(['yellow','pink', 'black' , 'black' , 'black' , 'white' , 'red', 'blue', 'green', 'purple', 'orange', 'grey', 'silver', 'gold' , '', ''])
    # leather = choice(['leather', 'latex', 'PVC', 'patent leather', 'faux leather', ''])
    # breakpoint()
    prompt, _ = random_line('seaart.txt')
    # breakpoint()
    sleep(2)
    def fill_prompt():
        dta = page.locator("#easyGenerateInput")
        dta.fill("")
        try:
            page.locator(".trigger-word-area-use-all").click(timeout=5000)
        except:
            pass
            # breakpoint()
        dta.fill( dta.input_value() + " " + prompt)
        print("Current prompt in input box:", dta.input_value())
        if not prompt in dta.input_value():
            fill_prompt()
        # dta.click()
    # sleep(5)
    fill_prompt()
    credits_required = int(page.locator(".generate-btn-sub").inner_text())
    credit_elem = page.locator("div.stamina:nth-child(1) > div:nth-child(2)")
    credits_available = int(credit_elem.inner_html())
    i = page.locator('div[data-event="generate_click_image_numbers"]').count() - 2
    page.locator('div[data-event="generate_click_image_numbers"]').nth(i+1).click()
    # breakpoint()
    while credits_available <= credits_required and i >= 0:
        print(f"Not enough credits to generate image. Available: {credits_available}, Required: {credits_required}")
        i -= 1
        page.locator('div[data-event="generate_click_image_numbers"]').nth(i).click()
        # fill_prompt()
        
        sleep(8)
        credits_available = int(credit_elem.inner_html())
        credits_required = int(page.locator(".generate-btn-sub").inner_text())
        # credits_available = int( page.locator(".number").first.inner_text())
    
    if i >= 0:    
        page.locator("#generate-btn").click()

def run(playwright: Playwright) -> None:
    userid = r'ash' 
    profile_dir = r'C:\dumpinggrounds\browserprofileff'
    discord_dir = r"C:\dumpinGGrounds\ffprofilediscord"
    download_path = os.path.abspath("seart_downloads")
    os.makedirs(download_path, exist_ok=True)
    dirs = [x for x in itertools.chain(Path(discord_dir).iterdir(), Path(profile_dir).iterdir()) if x.is_dir()]
    shuffle(dirs)
    image_dir = Path(r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\sea_art")

    for user in tqdm(dirs):
        if not user.is_dir():
            continue
        userid = user.name
        
        # if not 'diffusionstable877discord' in userid:
        #     print(f"Skipping user {userid} as it is a colab user")
        #     continue
        
        print(f"Using user ID: {userid}")
        # user_data_dir = Path(rf'{profile_dir}\{userid}')
        browser = playwright.firefox.launch_persistent_context(str(user),headless=True,downloads_path=download_path)
        page = browser.new_page()
        page.set_default_timeout(60000 * 2)
        # breakpoint()
        page.goto("https://www.seaart.ai")
        # breakpoint()
        # sleep(9000)
        for i in range(1):
            if not any(user.iterdir()):
                print(f"User directory {user} is empty.")
                breakpoint()
            
            # breakpoint()
            # if "sense" in userid:
            #     breakpoint()
            #     pass
            # else:
            #     print(f"Skipping user {userid} as it is not an image generation user")
            #     break
            #https://www.seaart.ai/create/video?id=3af4aa8d07e30b4a895b45771232f2bm&model_ver_no=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6
            try:
                page.goto("https://www.seaart.ai/create/video?id=3af4aa8d07e30b4a895b45771232f2bm&model_ver_no=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6")
                if page.locator(".user-daily-close > i:nth-child(1)").count() > 0:
                    page.locator(".user-daily-close > i:nth-child(1)").click()
                if page.locator(".gift-btn").count() < 1:
                    print("No gift button found, possibly out of credits.")
                    # breakpoint()
                    # break
                try:
                    page.locator(".gift-btn").click()
                except:
                    print("Could not click gift button, possibly out of credits.")
                    # breakpoint()
                    # break
                sleep(2)
                # breakpoint()
                # page.locator(".claim-button").first.click()
                if page.locator(".claim-button").count() < 1:
                    print("No claim button found, possibly out of credits.")
                    breakpoint()
                    break
                page.locator(".claim-button").last.click()
                page.goto("https://www.seaart.ai/create/video?id=3af4aa8d07e30b4a895b45771232f2bm&model_ver_no=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6")
                # breakpoint()
                sleep(2)
                # uploaded = page.locator(".image-box-mask").count()
                
                # breakpoint()
                if int( page.locator(".number").first.inner_text()) > 90 and False:
                    sel_img, prompt = get_random_image_and_prompt(image_dir)
                    sleep(2)
                    first = True
                    while  page.locator(".image-box-mask").count() == 0:
                        if not first:
                           sel_img.unlink() 
                        sel_img, prompt = get_random_image_and_prompt(image_dir)
                        page.locator(".el-upload__input").nth(1).set_input_files(str(sel_img))
                        sleep(15)
                        print(f"Waiting for image to upload...{page.locator('.image-box-mask').count()}",flush=True)
                        first = False

                    # page.locator("div.upload-change-item:nth-child(1)").click()
                    # page.locator(".video-upload > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)").click()
                    # while (page.locator(".el-upload__input").count() > 2):
                    sleep(2)
                    print("Image uploaded successfully")
                    dta = page.locator(".video-custom-textarea")
                    dta.click()
                    # prompt_file = sel_img.parent.with_suffix('.txt')
                    # prompt = prompt_file.read_text()
                    dta.fill(prompt)
                    # page.locator("#easyGenerateVideoInput").fill()
                    # page.locator("div.generate-btn:nth-child(4)").click()
                    # with page.expect_request("**/api/v1/task/detail", timeout=180000) as response_info:
                    # save_all_req_resp(page,f"seaart_{userid}_all_req_resp.log")
                    page.locator("div.generate-btn:nth-child(4)").click()
                    # sleep(180)
                    # response = response_info.value
                    # response_path = respinse_save_dir / f"{userid}_response.json"
                    # with open(response_path, "a+", encoding="utf-8") as f:
                    #     try:
                    #         resp_json = response.json()
                    #     except Exception:
                    #         resp_json = {"status": response.status, "url": response.url, "body": response.text()}
                    #     json.dump(resp_json, f, ensure_ascii=False, indent=2)
                    # print(f"Saved response info to {response_path}")
                    # sleep(60)
                # page.locator(".image-render-box").nth(0).hover()
                
                while int(page.locator("div.stamina:nth-child(1) > div:nth-child(2)").inner_html()) >= 10:
                        generate_images(page)
                download_videos(page)
                    # print("No image boxes found, possibly out of credits.")
                    # breakpoint()  
                    # break
                # else:
                # breakpoint()
                # raise Exception("This is a test exception to see if the error handling works")
                sleep(3)
            except Exception as e:
                page.screenshot(path=f"seart\\{userid}_error.png")
                print(f"An error occurred: {e}")
                print("An error occurred, retrying...with different user\n\n\n\n\n\n\n")
                break
        # breakpoint()
        sleep(3)
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