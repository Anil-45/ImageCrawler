"""Utils."""
import os
import base64
import concurrent.futures
import requests
import validators
import urllib3

from constants import MAX_WORKERS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_images(image_urls: list, obj_to_search: str, out_dir: str):
    """Download image from a source to required directory.

    Args:
        image_urls (list): List of image urls
        obj_to_search (str): search object
        out_dir (str): ouput directory
    """
    dir_path = f"{out_dir}/{obj_to_search}"
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    ## Function to download image
    def _download_img(url, ind):
        if url is None:
            return

        if validators.url(url):
            req = requests.get(url, stream=True, timeout=10, verify=False)
            if req.ok:
                image_content = req.content
            else:
                return
        else:
            img_encoded = url.split(",")[-1].strip()
            image_content = base64.b64decode(img_encoded)

        file_name = f"{dir_path}/img_{ind}.jpg"

        with open(file_name, "wb+") as img:
            img.write(image_content)

    ## Creating number of thread as per the images
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for ind, img_url in enumerate(image_urls):
            executor.submit(_download_img, img_url, ind)
