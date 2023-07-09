from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchFrameException

from urllib.parse import parse_qs

class Config:
    get_driver = None


def init_chrome_driver(get_driver=lambda: webdriver.Chrome()):
    """
    Initialize the chromedriver for use with gdown. This is required for
    downloading files from Google Drive that are restricted and
    require cookies to be set.
    """
    Config.get_driver = get_driver


def selenium_get_url_confirmation(view_url, quiet):
    """
    Get the cookies, video source URL and filename from a Google Drive URL.
    """
    url_args = parse_qs(view_url.split("?")[-1])
    view_url = (
        f"https://drive.google.com/file/d/{url_args['id'][0]}/view?usp=sharing"
    )
    if not quiet:
        print(f"Chromedriver fetching '{view_url}'")
    driver = Config.get_driver()
    driver.get(view_url)
    thumbnail = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "/html/body/div[3]/div[3]/div[4]/div[3]/div/div[2]/div[2]/div/div",
            )
        )
    )

    thumbnail.click()

    filename = driver.find_element(
        By.XPATH, "/html/body/div[3]/div[4]/div/div[1]/div[2]/div[1]"
    ).text
    filename = filename.replace("/", "_")
    if not quiet:
        print(f"Video filename found as '{filename}'")

    cookies = driver.get_cookies()

    for _ in range(10):
        iframe = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.ID, "drive-viewer-video-player-object-0")
            )
        )
        try:
            driver.switch_to.frame(iframe)
        except NoSuchFrameException:
            if not quiet:
                print("Frame not found, retrying...")
            import time

            time.sleep(3)
        else:
            if not quiet:
                print("Switched to video frame.")
            break

    player = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/div/div[1]/video")
        )
    )
    player.click()
    cookies = {cookie["name"]: cookie["value"] for cookie in cookies}
    video_src = player.get_attribute("src")
    return cookies, video_src, filename
