import os

from gdown.download import download
from gdown.webdriver_utils import init_chrome_driver


def test_download():
    url = "https://raw.githubusercontent.com/wkentaro/gdown/3.1.0/gdown/__init__.py"  # NOQA
    output = "/tmp/gdown_r"

    # Usage before https://github.com/wkentaro/gdown/pull/32
    assert download(url, output, quiet=False) == output
    os.remove(output)


def test_chrome_download():
    url = "https://drive.google.com/file/d/1GwjoIy9EE0Efjomce14MeBZQ5h41Gm09/view?usp=sharing"
    output = "meme.mp4"
    init_chrome_driver()

    assert download(url, fuzzy=True, quiet=False) == output
    os.remove(output)
