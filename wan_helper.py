from time import sleep
from playwright.sync_api import Page


def setup_image_to_video(
    page: Page,
    prompt: str,
    sel_img: str,
    available_credits: int,
    sleep_time: float = 1.0
):
    """
    Configure image-to-video generation based on available credits.

    Args:
        page (Page): Playwright page instance
        prompt (str): Prompt text to type
        sel_img (str): Image file path to upload
        available_credits (int): Remaining user credits
        sleep_time (float): Delay after file upload
    """
    try:
    # Select prompt box and enter prompt
        # page.locator('div', has_text="describe the action").last.click()
        page.locator('div[role="textbox"]').last.fill(prompt)
    except Exception as e:
        # print(f"Error typing prompt: {e}")
        page.locator('div', has_text="describe the action").last.type(prompt,delay=50)
        # breakpoint()
        pass

    # Select first frame and upload image
    page.locator('div[data-test-id="creation-form-box-undefined"]').first.click()
    with page.expect_file_chooser() as fc_info:
        page.locator('div[data-test-id="creation-form-box-upload"]').click()

    file_chooser = fc_info.value
    file_chooser.set_files(str(sel_img))
    sleep(sleep_time)

    page.locator('div[class*="SettingWrapper-sc"]').locator('div[class*="Content-"]').nth(1).click()
    try:
        if available_credits >= 45 or available_credits < 11:
            _select_model(page, "Wan2_6")
            
            _select_settings(page, "1080", "15")

        elif available_credits >= 20:
            _select_model(page, "Wan2_6")
            # _select_resolution(page, "640*480")
            # _select_duration(page, "10")
            _select_settings(page, "720", "10")

        elif available_credits >= 10:
            _select_model(page, "Wan2_5")
            _select_settings(page, "480", "10")
            # _select_model(page, "Wan2_2")
            # _select_resolution(page, "1280*720")

        
            
            # _select_duration(page, "10")
            # _select_resolution(page, "1920*1080")

    except Exception as e:
        print(f"Error selecting model/settings: {e}")
        # breakpoint()
        
        pass



def _select_model(page: Page, model_name: str):
    page.locator('div[data-test-id="creation-form-button-model"]').click()
    page.locator(f'div[data-test-id="creation-form-box-{model_name}"]').click()


def _select_settings(page: Page, resolution: str, duration: str):
    page.locator('div[class*="SettingWrapper-sc"]').locator('div[class*="Content-"]').nth(1).click()
    page.locator(f'div[title="{resolution}P"]').click()
    # page.locator(f'div[title="{resolution}P"]').click()
    page.locator(f'div[title="{duration}s"]').click()
    # page.locator(f'div[data-test-id="creation-form-box-{resolution}"]').click()


