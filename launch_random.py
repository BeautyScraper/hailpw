from random import choice, shuffle
import shutil
from playwright.sync_api import Playwright, sync_playwright, expect
from pathlib import Path
from scrapy.http import HtmlResponse
from time import sleep
import re
import json
from user_id import userids 
from os import listdir
from os.path import isdir, join
from datetime import datetime
from collections import defaultdict

img_dir = r'D:\paradise\stuff\essence\Pictures\Heaps\heap_Chudasi\1'
prompts = Path('prompt.txt').read_text().splitlines()
userid = r'sstico0'
to_download = True

def mainparse(urlt : str, browser,fp,prompt):
    # context = browser.new_context()
    wait_for_image_second = 15
    context = browser
    page = context.new_page()
    # page.on("request", lambda request: streamtapecall(request,filename))
    # page.on("response", lambda response: streamtapecall(response,filename))
    page.goto(urlt)
    # # with open("cookies.json", "w") as f:
    # #     f.write(json.dumps(context.cookies()))
    # breakpoint()
    sleep(3)
    # page.locator(".transition-all > svg").first.click()
    # sleep(3)
    if to_download:
        breakpoint()
    file_input = page.locator('input[type="file"][name="file"]')

    sleep(5)
    file_input.set_input_files(fp)
    # Wait until the file input is updated with the file path
    # breakpoint()

    while page.locator("div.relative.h-14.w-14.cursor-pointer.overflow-hidden.rounded-lg img").count() <= 0:
        print("Waiting for file input to be updated...")
        wait_for_image_second -= 1
        if wait_for_image_second <= 0:
            return
        sleep(1)
    # page.locator(".transition-all > svg").first.click()wwwwwwwwwwwwwwww
    print('Hello')
    # file_chooser = file_chooser_info.value
        # page.get_by_role("button", name="Upload").click()
    # file_chooser.set_files(fp)
    # sleep(15)
    page.get_by_placeholder("Type your idea, click 'Create' to get a video").fill(prompt)
    # breakpoint()
    # sleep(10)
    page.get_by_role("button", name="Create", exact=True).click()
    sleep(1)
    # filename = url.strip('/').split('/')[-1]

    # breakpoint()

    # filename = resp.css(".video-title::text").get()[:230] + '.mp4'
    # upat = '.+response-content-disposition.+' 
    # # upat = '.+mp4.+' 
    # page.locator("#player").get_by_role("button").last.click()
    # sleep(1)
    # with page.expect_request(lambda request: re.match(upat,request.url)) as first:
    #     page.locator("#player").get_by_role("button").first.click()
    #     # breakpoint()   
    # request = first.value
    # ariaDownload(request.url,ddir_path,filename)
    # list(map(lambda x:x.close(), context.pages[1:]))
    # print(first.value)    
    # sleep(60)
    # page.get_by_label("Play").click()
    # download(r'C:\Heaven\Haven\brothel\Sherawali', filename, url_t)

# https://lexica.art/prompt/ca7f2856-8f79-4aa8-85c0-45d3e1ef8939
# https://image.lexica.art/full_jpg/0509ff23-a646-4345-97b9-6a781fa6ed37

    # context.close()


def run(playwright: Playwright,user_data_dir) -> None:
    # browser = playwright.chromium.launch(headless=False)
    # user_data_dir = Path(rf'{profile_dir}\{userid}')
    
    # user_data_dir.mkdir(exist_ok=True,parents=True)
    # shutil.rmtree(user_data_dir)
    # user_data_dir.mkdir(exist_ok=True,parents=True)

    url = "https://hailuoai.video/"
    # browser = playwright.chromium.launch_persistent_context(user_data_dir,headless=False,proxy=proxy)
    browser = playwright.chromium.launch_persistent_context(user_data_dir,headless= not to_download,args=["--disable-blink-features=AutomationControlled"])
    # browser = browser.new_context(storage_state=f"{userid}.json")
    # create an array which contains all the file of a given deirectory using pathlib
    file_list = [f for f in Path(img_dir).rglob("*.jpg")] + [f for f in Path(img_dir).rglob("*.jpeg")] + [f for f in Path(img_dir).rglob("*.png")]
    # breakpoint()
    fp = choice(file_list) 
    pp = choice(prompts).strip()
    # file_list = os.listdir(r"C:\Personal\Games\Fapelo\hailuoai\Women Dancing Seductively")
    # loop through the array in batches of three
    mainparse(url, browser,str(fp),pp)
    # for i in range(0, len(file_list), 3):
    #     batch = file_list[i:i+3]
    #     for fp in batch:
    #         fp.unlink()
    #         # break
    #     break
    browser.close()

with sync_playwright() as playwright:
    profile_dir = r'C:\dumpinggrounds\browserprofile'
    # List all directories in profile_dir
    directories = [d for d in listdir(profile_dir) if isdir(join(profile_dir, d))]

    # Display directories to the user
    print("Available directories:")
    for idx, directory in enumerate(directories, start=1):
        print(f"{idx}. {directory}")

    # Ask the user to select a directory
    selected_indexs = list(range(len(directories)))
    # Validate the selection
    for si in selected_indexs:
        if 0 <= si < len(directories):
            userid = directories[si]
        else:
            raise ValueError("Invalid selection. Please run the script again and select a valid number.")
        user_data_dir = Path(rf'{profile_dir}\{userid}')
        # File to store processing history
        history_file = Path("processing_history.json")

        # Load processing history
        if history_file.exists():
            with open(history_file, "r") as f:
                processing_history = json.load(f)
        else:
            processing_history = defaultdict(list)

        # Check if the userid has been processed today
        today = datetime.now().strftime("%Y-%m-%d")
        if userid in processing_history:
            today_count = sum(1 for date in processing_history[userid] if date == today)
            if today_count >= 3:
                print(f"UserID {userid} has already been processed {today_count} times today. Skipping.")
                continue

        run(playwright,user_data_dir)
        # Update processing history
        if userid not in processing_history:
            processing_history[userid] = []
        processing_history[userid].append(today)
        with open(history_file, "w") as f:
            json.dump(processing_history, f)