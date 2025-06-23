from random import choice, shuffle
import shutil
from playwright.sync_api import Playwright, sync_playwright, expect
from pathlib import Path
from scrapy.http import HtmlResponse
from time import sleep, time
import re
import json
from user_id import userids , img_dir
from notSoRand import main as randomLine
from os import listdir
import os
from os.path import isdir, join
from aria2cgeneric import generic_downloader

prompt1 = "full body photo of blue skinned Bengali proportionately voluptuous goddess with multiple hands with big cleavage wearing bikini and stocking, wearing garland  made of skull"
def get_new_prompt():
    # This function should return a new prompt for the video creation
    # For now, we will return a static prompt
    prompt = randomLine()
    
    return prompt

def download_and_delete_image(page,index=1):
    breakpoint()
    download_path = os.path.abspath("downloads")
    
    with page.expect_download() as download_info:
        page.locator(f"div.group\/video-card:nth-child({index}) > section:nth-child(2) > div:nth-child(3) > div:nth-child(1) > button:nth-child(2)").first.click()
        # page.locator(".ant-dropdown-placement-topRight > ul:nth-child(1) > li:nth-child(1)").first.click()
    download = download_info.value
    extension = download.suggested_filename.split('.')[-1]
    if extension.lower() == '':
        extension = 'zip'
    rand_filename = f"{int(time())}.{extension}"
    # Save the downloaded file
    downloaded_file_path = download.path()
    print(f"Downloaded to temp: {downloaded_file_path}")
    download.save_as(os.path.join(download_path, rand_filename))
    print(f"Saved to: {os.path.join(download_path, download.suggested_filename)}")
    # breakpoint()
    page.locator(f"div.group\/video-card:nth-child(1) > section:nth-child(2) > div:nth-child(3) > div:nth-child(1) > button:nth-child(3)").first.click()
    try:
        page.locator(f"button.ant-btn:nth-child(2)").first.click()
    except Exception as e:  
        download_and_delete_image(page, index=index+1)
        


    # Save the downloaded file (optional if downloads_path is already set)
    
    # images = page.locator('img.allow-drag.h-full.cursor-pointer')
    # count = images.count()
    # for i in range(count):
    #     breakpoint()
    #     img = images.nth(i)
    #     img.hover()
    #     img.locator('button.ant-dropdown-trigger').hover()
    #     img.click('li.ant-dropdown-menu-item')

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
        download_and_delete_image(page)
def create_wait(page):
    for i in range(1,10):
        # prompt = get_new_prompt()
        # page.locator("#video-create-textarea").click()
        # page.locator("#video-create-textarea").fill(prompt)
        # page.get_by_role("button", name="4").click()
        # sleep(100)
        # breakpoint()
        try:
            download_and_delete_image(page)
        except:
            download_and_delete_image(page,index=2)
def delete_images(page):
    download_path = os.path.abspath("downloads_dreams")
    os.makedirs(download_path, exist_ok=True)
    sleep(10)
    page.locator("img[src*='medium']").last.click()
    breakpoint()
    src_list = page.locator("img[src*='public']").evaluate_all("elements => elements.map(el => el.src)")
    for iurl in src_list:
        generic_downloader(iurl, iurl.split('/')[-2]+'.jpg',iurl,1,download_path)
    page.locator("#radix-«r8b»").last.click()
    page.locator("body > div:nth-child(21)").last.click()
    page.locator("button.hover\:bg-white\/30:nth-child(2)").last.click()


def run(playwright: Playwright) -> None:
    userid = r'ash' 
    profile_dir = r'C:\dumpinggrounds\browserprofileff'
    download_path = os.path.abspath("downloads_dreams")
    os.makedirs(download_path, exist_ok=True)
    dirs = [x for x in Path(profile_dir).iterdir() if x.is_dir()]
    shuffle(dirs)
    for user in dirs:
        if not user.is_dir():
            continue
        userid = user.name
        print(f"Using user ID: {userid}")
        user_data_dir = Path(rf'{profile_dir}\{userid}')
        browser = playwright.firefox.launch_persistent_context(user_data_dir,headless=True,downloads_path=download_path)
        page = browser.new_page()
        
        page.goto("https://dream-machine.lumalabs.ai/ideas")
        # breakpoint()
        sleep(10)
        for i in range(1, 100):
            # prompt = get_new_prompt()
            prompt = "A mountain landscape with a river flowing through it, in the style of a watercolor painting"
            page.locator(".break-words").click()
            page.locator(".break-words").fill(prompt1)
            page.locator("button.relative").click()
            break
        sleep(10)
        delete_images(page)
        # src_list = page.locator("img[src*='medium']").evaluate_all("elements => elements.map(el => el.src)")
        # full_size = [x.replace("medium", "public") for x in src_list]
        # for iurl in full_size:
        #     # breakpoint()
        #     generic_downloader(iurl, iurl.split('/')[-2]+'.jpg',iurl,1,download_path)

        page.wait_for_timeout(10000)
        
        browser.close()

with sync_playwright() as playwright:
    run(playwright)