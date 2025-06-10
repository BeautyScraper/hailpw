import shutil
from playwright.sync_api import Playwright, sync_playwright, expect
from pathlib import Path
from scrapy.http import HtmlResponse
from time import sleep
import re
import json
from user_id import userids as userids

userid = r'alind' 

def mainparse(urlt : str, browser):
    # context = browser.new_context()
    context = browser
    page = context.new_page()
    # page.on("request", lambda request: streamtapecall(request,filename))
    # page.on("response", lambda response: streamtapecall(response,filename))
    page.goto(urlt,timeout=0)
    # # with open("cookies.json", "w") as f:
    # #     f.write(json.dumps(context.cookies()))

    breakpoint()
    # storage = context.storage_state(path=f"{userid}.json")
    sleep(500)
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

    context.close()


def run(playwright: Playwright) -> None:
    
    user_data_dir = Path(rf'C:\dumpinggrounds\browserprofileff\{userid}')
    # user_data_dir.mkdir(exist_ok=True,parents=True)
    # shutil.rmtree(user_data_dir)
    # user_data_dir.mkdir(exist_ok=True,parents=True)

    url = "https://hailuoai.video"
    # browser = playwright.chromium.launch_persistent_context(user_data_dir,headless=False,proxy=proxy)
    browser = playwright.firefox.launch_persistent_context(user_data_dir,headless=False)
    # browser = browser.new_context(storage_state=f"{userid}.json")
    mainparse(url, browser)
    browser.close()

with sync_playwright() as playwright:
    run(playwright)