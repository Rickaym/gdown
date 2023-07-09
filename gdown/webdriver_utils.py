import os.path as osp
from os import makedirs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchFrameException

from urllib.parse import parse_qs

INITIALIZED = False
_DRIVER: webdriver.Chrome = None  # type: ignore

def init_chrome_driver(get_driver=lambda: webdriver.Chrome()):
    global _DRIVER, INITIALIZED
    INITIALIZED = True
    _DRIVER = get_driver()

def selenium_get_url_confirmation(view_url, quiet):
    # Parse the URL into components
    url_args = parse_qs(view_url.split('?')[-1])
    view_url = f"https://drive.google.com/file/d/{url_args['id'][0]}/view?usp=sharing"
    if not quiet:
        print(f"Chromedriver fetching '{view_url}'")
    _DRIVER.get(view_url)
    thumbnail = WebDriverWait(_DRIVER, 60).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "/html/body/div[3]/div[3]/div[4]/div[3]/div/div[2]/div[2]/div/div",
            )
        )
    )

    thumbnail.click()

    filename = _DRIVER.find_element(
        By.XPATH, "/html/body/div[3]/div[4]/div/div[1]/div[2]/div[1]"
    ).text
    filename = filename.replace("/", "_")
    if not quiet:
        print(f"Video filename found as '{filename}'")

    cookies = _DRIVER.get_cookies()

    for _ in range(10):
        iframe = WebDriverWait(_DRIVER, 30).until(
            EC.presence_of_element_located((By.ID, "drive-viewer-video-player-object-0"))
        )
        try:
            _DRIVER.switch_to.frame(iframe)
        except NoSuchFrameException:
            if not quiet:
                print("Frame not found, retrying...")
            import time
            time.sleep(3)
        else:
            if not quiet:
                print("Switched to video frame.")
            break

    player = WebDriverWait(_DRIVER, 30).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[1]/video"))
    )
    player.click()
    cookies = {cookie["name"]: cookie["value"] for cookie in cookies}
    video_src = player.get_attribute("src")
    return cookies, video_src, filename