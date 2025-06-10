import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://hailuoai.video/create?_rsc=11c8k")
    page.locator("div").filter(has_text=re.compile(r"^VideoImage$")).get_by_role("img").nth(1).click()
    page.locator("#video-create-textarea").click()
    page.locator("#video-create-textarea").fill("Create an image")
    page.get_by_text("Image-0116:9").click()
    page.locator("div").filter(has_text=re.compile(r"^Image-0116:9$")).locator("span").nth(2).click()
    page.get_by_text("9:16").click()
    page.get_by_role("button", name="AI Video create png by Hailuo AI Video Generator Create").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
