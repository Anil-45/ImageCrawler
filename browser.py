"""Defines browser related operations."""
import time
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

from constants import (
    HREF,
    IMG_FULL_XPATH,
    MAX_SUGGESTIONS,
    MAX_WORKERS,
    PAGE_HEIGHT_QUERY,
    SEARCH_URL,
    SHOW_MORE_BUTTON,
    SRC,
    THUMBNAILS_XPATH,
)


def get_driver(headless: bool = False) -> webdriver:
    """Webdriver instance."""
    options = webdriver.ChromeOptions()
    options.headless = headless
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    web_driver = webdriver.Chrome(
        executable_path=ChromeDriverManager().install(), options=options
    )
    return web_driver


def _scroll_to_end(web_driver: webdriver, sleep: int):
    page_prev_height = web_driver.execute_script(PAGE_HEIGHT_QUERY)
    is_page_end = False
    while is_page_end is not True:
        time.sleep(sleep)
        page_cur_height = web_driver.execute_script(PAGE_HEIGHT_QUERY)
        if page_prev_height == page_cur_height:
            is_page_end = True
        else:
            page_prev_height = page_cur_height
        try:
            web_driver.execute_script(
                f"document.querySelector('.{SHOW_MORE_BUTTON}').click();"
            )
        except Exception as _:
            continue


def _get_page_urls(web_driver: webdriver, obj: str) -> set:
    page_urls = set()
    query = SEARCH_URL.format(q=obj.strip())
    page_urls.add(query)
    pattern = query.split("&", maxsplit=1)[0]
    web_driver.get(query)
    content = web_driver.find_elements_by_tag_name("a")
    for element in content:
        tag = str(element.get_attribute(HREF))
        if pattern in tag:
            page_urls.add(tag)
        if len(page_urls) > MAX_SUGGESTIONS:
            break
    return page_urls


def _get_img_urls(
    web_driver: webdriver, page_url: str, ind: int, timeout: int = 5
) -> set:
    img_srcs = set()
    WebDriverWait(web_driver, timeout)
    try:
        web_driver.get(page_url)
        time.sleep(1)
        _scroll_to_end(web_driver=web_driver, sleep=1)

        thumbnails = web_driver.find_elements(By.XPATH, THUMBNAILS_XPATH)
        for thumbnail in tqdm(thumbnails, leave=False, desc=f"PAGE_{ind}"):
            try:
                thumbnail.click()
                images = web_driver.find_elements(By.XPATH, IMG_FULL_XPATH)
                for image in images:
                    src = image.get_attribute(SRC)
                    img_srcs.add(src)
            except Exception as _:
                continue
    except Exception as _:
        pass

    return img_srcs


def extract_urls(web_driver: webdriver, obj: str, max_urls: int) -> list:
    """Extract the image source for download.

    Args:
        web_driver (webdriver): WebDriver instance
        obj (str): search string

    Returns:
        list: list of urls
    """
    img_srcs = set()
    page_urls = _get_page_urls(web_driver=web_driver, obj=obj)
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for ind, page_url in enumerate(page_urls):
            future = executor.submit(_get_img_urls, web_driver, page_url, ind)
            img_srcs.update(future.result())
            if len(img_srcs) > max_urls:
                break

    return list(img_srcs)
