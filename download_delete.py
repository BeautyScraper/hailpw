from random import choice
import shutil
from playwright.sync_api import Playwright, sync_playwright, expect
from pathlib import Path
from scrapy.http import HtmlResponse
from time import sleep, time
import re
import json
from user_id import userids , img_dir
from os import listdir
import os
from os.path import isdir, join


def get_new_prompt():
    # This function should return a new prompt for the video creation
    # For now, we will return a static prompt
    colors = ["red", "blue", "green", "yellow", "purple", "pink", "orange", "black", "white", "gray" , "golden", "silver"]
    return f"voluptuous bengali bride with showing cleavage in {choice(colors)} latex bikini stocking and glubs"

def download_and_delete_image(page,index = 1):
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
    # 
    page.locator(f"div.group\/video-card:nth-child(1) > section:nth-child(2) > div:nth-child(3) > div:nth-child(1) > button:nth-child(3)").first.click()
    page.locator(f"button.ant-btn:nth-child(2)").first.click()
        


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
    for i in range(1,100):
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



def run(playwright: Playwright) -> None:
    userid = r'sstico0' 
    profile_dir = r'C:\dumpinggrounds\browserprofileff'
    download_path = os.path.abspath("downloads")
    os.makedirs(download_path, exist_ok=True)
    user_data_dir = Path(rf'{profile_dir}\{userid}')
    browser = playwright.firefox.launch_persistent_context(user_data_dir,headless=False,downloads_path=download_path)
    page = browser.new_page()
    
    # breakpoint()
    page.goto("https://hailuoai.video/create?_rsc=11c8k")
    page.locator("div").filter(has_text=re.compile(r"^VideoImage$")).get_by_role("img").nth(1).click()
    
    # page.get_by_text("Image-0116:9").click()

    page.locator("div").filter(has_text=re.compile(r"^Image-0116:9$")).locator("span").nth(2).click()
    # breakpoint()
    page.get_by_text("9:16").last.click()
    create_and_wait(page)
    page.wait_for_timeout(10000)
    
    browser.close()

with sync_playwright() as playwright:
    run(playwright)