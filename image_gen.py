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


def get_new_prompt():
    # This function should return a new prompt for the video creation
    # For now, we will return a static prompt
    prompt = randomLine()
    
    return prompt

def download_cleansing(page):
    # breakpoint()
    page.locator("button.px-2\.5:nth-child(2)").click()
    image_grid = page.locator("div.grid-video-card").all()
    for im in image_grid:
        elem = im.locator("div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)")
        try:
            if "absolute right-[10px]" in elem.get_attribute("class"):
                elem.click()
                page.locator("button.ant-btn:nth-child(2)").first.click()
            else:
                print("No more images to delete")
                break
        except Exception as e:
            print(f"Error during deletion: {e}")
            # If an error occurs, we can try to delete the next image
            break
    page.locator("button.px-2\.5:nth-child(1)").click()

def download_and_delete_image(page,index=1):
    # breakpoint()
    page.locator("button.px-2\.5:nth-child(1)").click()
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
    sleep(20)
    page.locator(f"div.group\/video-card:nth-child(1) > section:nth-child(2) > div:nth-child(3) > div:nth-child(1) > button:nth-child(3)").first.click()
    page.locator(f"button.ant-btn:nth-child(2)").first.click()
    # try:
    # except Exception as e:  
    #     # download_cleansing(page)
    #     download_and_delete_image(page, index=index+1)
        


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
        try:
            download_and_delete_image(page)
        except Exception as e:
            print(f"Error during download: {e}")
            download_cleansing(page)
            continue


def run(playwright: Playwright) -> None:
    userid = r'ash' 
    profile_dir = r'C:\dumpinggrounds\browserprofileff'
    download_path = os.path.abspath("downloads")
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
        page.set_default_timeout(60000)
        
        # breakpoint()
        page.goto("https://hailuoai.video/create?_rsc=11c8k")
        page.locator("div").filter(has_text=re.compile(r"^VideoImage$")).get_by_role("img").nth(1).click()
        
        # page.get_by_text("Image-0116:9").click()

        page.locator("div").filter(has_text=re.compile(r"^Image-0116:9$")).locator("span").nth(2).click()
        # breakpoint()
        page.get_by_text("9:16").last.click()
        try:
            create_and_wait(page)
        except Exception as e:
            page.screenshot(path=f"ss\\{userid}_error.png")
            print(f"Error during creation: {e}")
            # Optionally, you can log the error or take a screenshot
            page.screenshot(path=f"{userid}_error.png")
            continue
        page.wait_for_timeout(10000)
        
        browser.close()

with sync_playwright() as playwright:
    run(playwright)