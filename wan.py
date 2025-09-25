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
import requests
from image_prompt import get_random_image_and_prompt


def download_video(video_url, videoid, download_dir, filename):
    download_path = Path(download_dir) / filename
    records_file =  Path("downloaded_records.txt")
    # Check if already downloaded by videoid in records file
    already_downloaded = False
    if records_file.exists():
        with records_file.open("r") as f:
            if videoid in [line.strip() for line in f]:
                already_downloaded = True
    if already_downloaded or download_path.exists():
        # print(f"Video {videoid} already downloaded (checked with records file).")
        return True

    # Use requests to download the video reliably
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        with open(download_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded video to {download_path}")
        # Record the download by videoid
        with records_file.open("a") as f:
            f.write(videoid + "\n")
        return True
    else:
        # print(f"Failed to download video from {video_url}, status code: {response.status_code}")
        return False
        breakpoint()

def download_files(page):
    download_dir = os.path.abspath(r"seart_downloads\mp4s")
    sleep(5)
    params = page.locator('#tb-beacon-aplus').get_attribute('exparams') 
    match = re.search(r'userid=(\d+)', params)
    wanuserid = match.group(1) if match else None
    for vdiv,prompt in zip(page.locator('div.infinite-scroll-component').locator('div[id*="__"]').all(), page.locator(".prompt-tooltip").all()):
        video_id = vdiv.get_attribute('id').split('__')[0]
        template_url = f"https://cdn.wanxai.com/wanx/{wanuserid}/image_to_video/{video_id}.mp4"
        # breakpoint()
        filename = f"wan_{wanuserid}_{video_id}.mp4"
        x = download_video(template_url, video_id, download_dir, filename)
        if not x:
            template_url2 = f"https://cdn.wanxai.com/wanx/{wanuserid}/video_extension/{video_id}.mp4"
            download_video(template_url2, video_id, download_dir, filename)
        if not Path(download_dir, filename).with_suffix('.txt').exists():
            Path(download_dir, filename).with_suffix('.txt').write_text(prompt.inner_text())

        
    # breakpoint()



def generate_video(page, name):
    page.goto("https://create.wan.video/generate")
    sleep(5)
    if page.locator('button', has_text='Get Member').count() > 0  or page.locator('div', has_text='Estimated time').count() > 0:
        return
    img_dir = r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan"
    sel_img, prompt = get_random_image_and_prompt(img_dir)
    page.locator('div', has_text= "image and describe").last.click() 
    page.locator('div', has_text= "image and describe").last.type(prompt)
    page.locator('div[data-test-id="creation-form-box-First Frame"]').click()
    with page.expect_file_chooser() as fc_info:
        page.locator('div[data-test-id="creation-form-box-upload"]').click()   
    # page.locator('input[type="file"]').set_input_files(str(sel_img))
    file_chooser = fc_info.value
    file_chooser.set_files(str(sel_img))
    sleep(1)
    try:
        if int( page.locator("[data-test-id=\"header-popover-button-credit\"]").inner_text()) < 1:
            # print("Not enough credits to generate video.")
            page.locator('div[data-test-id="creation-form-button-duration"]').click()
            page.locator('div[data-test-id="creation-form-box-10"]').click() 
            page.locator('div[data-test-id="creation-form-button-resolution"]').click()
            page.locator('div[data-test-id="creation-form-box-1920*1080"]').click()
    except:
        pass
    # breakpoint()
    sleep(3)
    page.locator('div[data-test-id="creation-form-button-submit"]').click()
    sleep(2)
    try:
        page.locator('button', has_text='ccelerate').click(timeout=1000)
    except:
        print("No accelerate button found.")
    # breakpoint()
    sleep(2)
    # breakpoint()
    generate_video(page, name)
    
def claim_free_credits(page):
    # breakpoint()
    page.locator(".checkInGuidePopover").click()
    try:
        page.locator("button.ant-btn:nth-child(3)").click(timeout=2000)
    except:
        print("No free credits to claim.")

    page.locator(".ant-btn-sm").count() > 0 and page.locator(".ant-btn-sm").click(timeout=1000)



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
        browser = playwright.firefox.launch_persistent_context(str(user),headless=False,downloads_path=download_path)
        # user_data_dir = Path(rf'{profile_dir}\{userid}')
        page = browser.new_page()
        page.set_default_timeout(30000)
        page.goto("https://create.wan.video/generate")
        # breakpoint()
        claim_free_credits(page)
        generate_video(page, userid)
        download_files(page)

        
        browser.close()
        continue
       

with sync_playwright() as playwright:
    run(playwright)

# describe the image as a prompt to generate similar images give especial focus to the intricacies of the dress please remember i am not asking you to generate image i want to to give me prompt
# describe the image as a prompt to generate similar images please remember i am not asking you to generate image i want to to give me prompt