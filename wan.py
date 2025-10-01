import itertools
import profile
from random import choice, shuffle
import shutil
import pandas as pd
from playwright.sync_api import Playwright, sync_playwright, expect
from pathlib import Path
from scrapy.http import HtmlResponse
from time import sleep, time
import re
import json
import pyperclip

import tqdm
from user_id import userids , img_dir
from notSoRand import random_line
from os import listdir
import os
from os.path import isdir, join
import requests
from image_prompt import get_random_image_and_prompt,input_with_timeout
from oldest_time import update_oldest_datetime

allow_rerun = False
prompt_checking = False
force_gui = False


if prompt_checking:
    force_gui=True
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

def download_files(page, name='wan'):
    download_dir = os.path.abspath(r"seart_downloads\mp4s")
    sleep(5)
    params = page.locator('#tb-beacon-aplus').get_attribute('exparams') 
    match = re.search(r'userid=(\d+)', params)
    wanuserid = match.group(1) if match else None
    downloaded_something = False
    for vdiv,prompt in zip(page.locator('div.infinite-scroll-component').locator('div[id*="__"]').all(), page.locator('span.prompt-tooltip').all()):
        video_id = vdiv.get_attribute('id').split('__')[0]
        template_url = f"https://cdn.wanxai.com/wanx/{wanuserid}/image_to_video/{video_id}.mp4"
        # breakpoint()
        filename = f"{video_id}_{name}_{wanuserid}.mp4"
        x = download_video(template_url, video_id, download_dir, filename)
        if x:
            downloaded_something = True
        if not x:
            template_url2 = f"https://cdn.wanxai.com/wanx/{wanuserid}/video_extension/{video_id}.mp4"
            download_video(template_url2, video_id, download_dir, filename)
        if not Path(download_dir, filename).with_suffix('.txt').exists() and Path(download_dir, filename).exists():
            # breakpoint()
            page.locator('body').click()
            prompt.hover()

            # page.locator('span.prompt-tooltip').first.focus()
            sleep(3)
            # message =  page.locator('div.ant-tooltip-inner[role="tooltip"]').last.inner_text()
            

            # if len(message) <= 3 :
            rt = prompt.inner_text()
            message = page.locator('div', has_text=rt).last.inner_text()
            Path(download_dir, filename).with_suffix('.txt').write_text(message)
            
    return downloaded_something

        
    # breakpoint()

def infinite_video(page):
    if page.locator('div.infinite-scroll-component').locator('div[id*="__"]').nth(0).locator('video').count() == 0 and download_files(page):
        print('last one was porn')
        page.locator('button', has_text="rerun").first.click()
        page.locator('button', has_text='ccelerate').click(timeout=10000)
    while page.locator('div', has_text='Estimated time').count() > 0:
        sleep(3)
        
        # breakpoint()
    if page.locator('div', has_text='ust a moment').count() > 0:
        print("wait for just a moment to finish")
        sleep(20)

def generate_video(page, name):
    if page.url != "https://create.wan.video/generate":
        print("reloading page to check status")
        sleep(5)
    sleep(1)
    while page.locator('div', has_text='Estimated time').count() > 0:
        print('Video generated Estimated time')
        sleep(3)
        return
        
    # breakpoint()
    retries = 10
    while page.locator('div', has_text='ust a moment').count() > 0 and retries > 0:
        retries -= 1
        print("wait for just a moment to finish")
        sleep(3)
    if page.locator('div.infinite-scroll-component').locator('div[id*="__"]').nth(0).locator('video').count() == 0 and download_files(page,name) and  page.locator('button', has_text='Get Member').count() == 0 and allow_rerun:
        print('last one was porn')
        page.locator('button', has_text="rerun").first.click()
        try:
            page.locator('button', has_text='ccelerate').click(timeout=10000)
        except:
            pass
        # return
        # download_files(page)
    if page.locator('button', has_text='Get Member').count() > 0  or page.locator('div', has_text='Estimated time').count() > 0 or page.locator('div', has_text='Just a moment').count() > 0:
        if not prompt_checking:
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
        # breakpoint()
        if available_credits >= 20:

            page.locator('div[data-test-id="creation-form-button-model"]').click()
            page.locator('div[data-test-id="creation-form-box-Wan2_5"]').click()
            page.locator('div[data-test-id="creation-form-button-resolution"]').click()
            page.locator('div[data-test-id="creation-form-box-1280*720"]').click()
            page.locator('div[data-test-id="creation-form-button-duration"]').click()
            page.locator('div[data-test-id="creation-form-box-10"]').click()
        elif available_credits >= 10:

            page.locator('div[data-test-id="creation-form-button-model"]').click()
            page.locator('div[data-test-id="creation-form-box-Wan2_5"]').click()
            page.locator('div[data-test-id="creation-form-button-resolution"]').click()
            page.locator('div[data-test-id="creation-form-box-640*480"]').click()
            page.locator('div[data-test-id="creation-form-button-duration"]').click()
            page.locator('div[data-test-id="creation-form-box-10"]').click()
            
            
            # breakpoint()
        elif available_credits >= 5:

            page.locator('div[data-test-id="creation-form-button-model"]').click()
            page.locator('div[data-test-id="creation-form-box-Wan2_2"]').click()
            page.locator('div[data-test-id="creation-form-button-resolution"]').click()
            page.locator('div[data-test-id="creation-form-box-1280*720"]').click()
            # breakpoint()
        elif available_credits < 1:
            # print("Not enough credits to generate video.")
            page.locator('div[data-test-id="creation-form-button-duration"]').click()
            page.locator('div[data-test-id="creation-form-box-10"]').click() 
            page.locator('div[data-test-id="creation-form-button-resolution"]').click()
            page.locator('div[data-test-id="creation-form-box-1920*1080"]').click()
            # return
    except:
        pass
    if prompt_checking:
        breakpoint()
    # breakpoint()
    sleep(3)
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
    # if int( page.locator("[data-test-id=\"header-popover-button-credit\"]").inner_text()) > 5:
    #     return
    page.locator(".checkInGuidePopover").first.click()
    try:
        page.locator("button.ant-btn:nth-child(3)").click(timeout=2000)
    except:
        print("No free credits to claim.")
    # try:
    #     page.locator(".ant-btn-sm").count() > 0 and page.locator(".ant-btn-sm").click(timeout=1000)
    # except:
    #     print("No small button to click.")



def run(playwright: Playwright) -> None:
    userid = r'ash' 
    headless = True
    global prompt_checking
    # if prompt_checking:
    #     headless = False
    profile_dir = r'C:\dumpinggrounds\browserprofileff'
    discord_dir = r"C:\dumpinGGrounds\ffprofilediscord"
    github = r"C:\dumpinGGrounds\ffgithub"
    tempmail = r"C:\dumpinGGrounds\tempmailsffprofile"
    cellular = r"C:\dumpinGGrounds\ffcellular"
    # profile_dirs = [profile_dir, discord_dir, github, tempmail]
    download_path = os.path.abspath("gemni_downloads")
    os.makedirs(download_path, exist_ok=True)
    # dirs = [x for x in itertools.chain( Path(profile_dir).iterdir(), Path(github).iterdir()) if x.is_dir()]
    # dirs = [x for x in itertools.chain( Path(profile_dir).iterdir(), Path(github).iterdir(), Path(discord_dir).iterdir(), Path(tempmail).iterdir()) if x.is_dir()]
    dirs = [x for x in itertools.chain( Path(cellular).iterdir()) if x.is_dir()]
    shuffle(dirs)
    exclude_user = []
    exclude_user_file = Path("exclude_user.txt")
    # if prompt_checking:
    #     headless = True
    ip = input_with_timeout("Select 1 \n1. GUI ON \n2. Stop before submission \n3. Delete excluding file \n4. stop at login screen\ninput:", 20,"n").lower()
    if '1' in ip:
        headless = False
    if '2' in ip:
        prompt_checking = True
    if  '3' in ip:
        exclude_user_file.unlink()
    if '4' in ip:
        stop_at_login = True
    else:
        stop_at_login = False
    while True:
        if exclude_user_file.exists():
            with exclude_user_file.open("r", encoding="utf-8") as f:
                exclude_user = [line.strip() for line in f if line.strip()]
            # dirs = [d for d in dirs if f'{d.parent}\\{d.name}' not in exclude_user]
            dirs = [d for d in dirs if str(d) not in exclude_user]
            # breakpoint()
            if len(dirs) < 1:
                break
        for user in tqdm.tqdm(dirs):
            # print(f'{user.parent}\\{user.name}')
            if not user.is_dir():
                continue
            
            userid = user.name
            print(f"Using user ID: {userid}")
            # if  'ffgithub' not in str(user) or 'temp' not in str(user):
            # if not 'browserprofileff\sstico1'  in str(user):
            #     continue
            # if not 'cell_ghost9'  in str(user):
            #     continue
            if f'{user.parent}\\{user.name}' in exclude_user:

                continue
            if force_gui:
                headless = False
            browser = playwright.firefox.launch_persistent_context(str(user),headless=headless,downloads_path=download_path)
            # user_data_dir = Path(rf'{profile_dir}\{userid}')
            page = browser.new_page()
            page.set_default_timeout(30000)
            page.goto("https://create.wan.video/generate")
            if stop_at_login:
                breakpoint()
            sleep(3)
            if page.locator('button', has_text='Get Member').count() > 0 and not prompt_checking:
                print(f'excluded_{user.parent}\\{user.name}')
                exclude_user.append(f'{user.parent}\\{user.name}')
                with exclude_user_file.open("a", encoding="utf-8") as f:
                    f.write(f'{user.parent}\\{user.name}\n')
                    # f.flush()
            # sleep(500)
            # browser.close()
            # continue
            # if 'ffprofilediscord' in str(user):
            # sleep(9000)
            claim_free_credits(page)
            generate_video(page, userid)
            # download_files(page)

            update_oldest_datetime([x.inner_text() for x  in page.locator('span', has_text="2025").all()[:1]])
            
            browser.close()
        wait_for = 1
        if len(dirs) <= 7:
            wait_for = 7
        for i in range(wait_for,0,-1):
            sleep( 60)
            print(f'{i} \n',end='',flush=True)
        # continue
       

with sync_playwright() as playwright:
    run(playwright)

# describe the image as a prompt to generate similar images give especial focus to the intricacies of the dress please remember i am not asking you to generate image i want to to give me prompt
# describe the image as a prompt to generate similar images please remember i am not asking you to generate image i want to to give me prompt