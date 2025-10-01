import itertools
import profile
from random import choice, randint, shuffle
import shutil
import pandas as pd
from playwright.sync_api import Playwright, sync_playwright, expect
from pathlib import Path
from scrapy.http import HtmlResponse
from time import sleep, time
import re
import json

import tqdm
from user_id import userids , img_dir
from notSoRand import random_line
from os import listdir
import os
from os.path import isdir, join
import requests
from image_prompt import get_random_image_and_prompt
from oldest_time import update_oldest_datetime


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
        if not Path(download_dir, filename).with_suffix('.txt').exists() and Path(download_dir, filename).exists():
            Path(download_dir, filename).with_suffix('.txt').write_text(prompt.inner_text())

        
    # breakpoint()



def generate_video(page, name):
    if page.url != "https://create.wan.video/generate":
        print("reloading page to check status")
        sleep(5)
    sleep(1)
    while page.locator('div', has_text='Estimated time').count() > 0:
        sleep(3)
        
        # breakpoint()
    if page.locator('div', has_text='ust a moment').count() > 0:
        print("wait for just a moment to finish")
        sleep(10)
        download_files(page)
    if page.locator('button', has_text='Get Member').count() > 0  or page.locator('div', has_text='Estimated time').count() > 0 or page.locator('div', has_text='Just a moment').count() > 0:
        return
    img_dir = r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan"
    page.goto("https://create.wan.video/generate")
    sleep(5)
    sel_img, prompt = get_random_image_and_prompt(img_dir)
    # try:
    page.locator('div', has_text= "image and describe").last.click() 
    page.locator('div', has_text= "image and describe").last.type(prompt)
    # except:
    #     print("Could not set prompt, skipping.")
    #     breakpoint()
    page.locator('div[data-test-id="creation-form-box-First Frame"]').click()
    with page.expect_file_chooser() as fc_info:
        page.locator('div[data-test-id="creation-form-box-upload"]').click()   
    # page.locator('input[type="file"]').set_input_files(str(sel_img))
    file_chooser = fc_info.value
    file_chooser.set_files(str(sel_img))
    sleep(1)
    try:
        available_credits = int( page.locator("[data-test-id=\"header-popover-button-credit\"]").inner_text())
        if available_credits < 1:
            # print("Not enough credits to generate video.")
            page.locator('div[data-test-id="creation-form-button-duration"]').click()
            page.locator('div[data-test-id="creation-form-box-10"]').click() 
            page.locator('div[data-test-id="creation-form-button-resolution"]').click()
            page.locator('div[data-test-id="creation-form-box-1920*1080"]').click()
        elif available_credits >= 5:

            page.locator('div[data-test-id="creation-form-button-model"]').click()
            page.locator('div[data-test-id="creation-form-box-Wan2_2"]').click()
            page.locator('div[data-test-id="creation-form-button-resolution"]').click()
            page.locator('div[data-test-id="creation-form-box-1280*720"]').click()
            # breakpoint()
    except:
        pass
    sleep(3)
    # breakpoint()
    with page.expect_response("**/api/common/imageGen") as response_info:
        page.locator('div[data-test-id="creation-form-button-submit"]').click()
    response = response_info.value
    if  'errorMsg' in response.json():
        if 'Please try a different image' in response.json()['errorMsg']:
            print("Image rejected, skipping.")
            sel_img.unlink()
        elif 'prompt' in response.json()['errorMsg']:
            # breakpoint()
            neg_prompt_file = Path(img_dir, 'negative_prompts').with_suffix('.neg.txt')
            with open(neg_prompt_file, "a", encoding="utf-8") as f:
                f.write(prompt + "\n")
            # return
        # return
        else:
            print(f"Error generating video: {response.json()['errorMsg']}")
            # breakpoint()
            # return
    else:
        pass
        # breakpoint()
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
    page.locator(".checkInGuidePopover").first.click()
    try:
        page.locator("button.ant-btn:nth-child(3)").click(timeout=2000)
    except:
        print("No free credits to claim.")
    try:
        page.locator(".ant-btn-sm").count() > 0 and page.locator(".ant-btn-sm").click(timeout=1000)
    except:
        print("No small button to click.")

def register(browser, page):
        sleep(5)
        if page.locator('span', has_text='Sign up').count() < 1:
            return
        page2 = browser.new_page()
        page2.set_default_timeout(120000)
        page2.goto("https://tempmailo.com/")
        # page2.locator('button', has_text='Change').first.click()
        page2.locator('button', has_text='Copy').click()
        pwd = 'c6556Bhg47w5PYCv'
        usrname = f'ghtyrt{randint(100, 999)}' 
        page.locator('span', has_text='Sign up').click()
        f = page.locator('div.ant-form-item.ant-form-item-vertical').locator('.ant-input') 
        f.nth(0).fill(usrname)
        f.nth(1).focus()
        page.keyboard.press("Control+V")
        f.nth(2).fill(pwd)
        f.nth(3).fill(pwd)
        sleep(10)
        page.locator('button', has_text = 'continue').click()
        sleep(15)
        message = 'heloo'
        while not 'verification code within' in message:
            page2.locator('.mail-item').first.click()
            message = page2.frame_locator("#fullmessage").locator("body").inner_text()
            sleep(2)
        # breakpoint()
        # try:
        # except:
        #     pass
        otp = re.search('\d{6}', message).group(0)
        page.locator('input.ant-input').fill(otp) 
        sleep(2)
        page.locator('button', has_text = 'continue').click()
        # breakpoint()


def run(playwright: Playwright) -> None:
    userid = r'ash' 
    profile_dir = r'C:\dumpinggrounds\browserprofileff'
    discord_dir = r"C:\dumpinGGrounds\ffprofilediscord"
    github = r"C:\dumpinGGrounds\ffgithub"
    tempmail = r"C:\dumpinGGrounds\tempmailsffprofile"
    cellular = r"C:\dumpinGGrounds\ffcellular"
    # profile_dirs = [profile_dir, discord_dir, github, tempmail]
    download_path = os.path.abspath("gemni_downloads")
    os.makedirs(download_path, exist_ok=True)
    dirs = [x for x in Path(cellular).iterdir() if x.is_dir()]
    shuffle(dirs)

    for user in tqdm.tqdm(dirs):

        if not user.is_dir():
            continue
        
        userid = user.name
        print(f"Using user ID: {userid}")
        # if  'ffgithub' not in str(user) or 'temp' not in str(user):
        # if not 'alindn755'  in str(user):
        #     continue


        #     continue
        browser = playwright.firefox.launch_persistent_context(str(user),headless=False,downloads_path=download_path)
        # user_data_dir = Path(rf'{profile_dir}\{userid}')

        page = browser.new_page()
        page.set_default_timeout(120000)
        page.goto("https://create.wan.video/generate")
        register(browser, page)
        breakpoint()
        claim_free_credits(page)
        sleep(5)

        browser.close()
        continue
        # if 'ffprofilediscord' in str(user):
        # sleep(9000)
        generate_video(page, userid)
        download_files(page)

        update_oldest_datetime([x.inner_text() for x  in page.locator('span', has_text="2025").all()[:1]])
        
        browser.close()
        continue
       

with sync_playwright() as playwright:
    run(playwright)

# describe the image as a prompt to generate similar images give especial focus to the intricacies of the dress please remember i am not asking you to generate image i want to to give me prompt
# describe the image as a prompt to generate similar images please remember i am not asking you to generate image i want to to give me prompt