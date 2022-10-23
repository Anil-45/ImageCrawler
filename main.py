"""Image Crawler."""
import argparse
import os
from tqdm import tqdm
from browser import extract_urls, get_driver
from constants import DEFAULT_IMG_COUNT
from logger import AppLogger
from utils import download_images


def crawl(args: argparse):
    """Crawl images."""
    obj_to_search = [obj.strip() for obj in args.object.split(",")]
    if 0 == len(obj_to_search):
        LOG.info("Please specify atleast one object")
        return

    LOG.info("%s Image Crawler %s", "*" * 10, "*" * 10)
    LOG.info("Scraping for: %s", obj_to_search)
    LOG.info("Output Dir: %s", args.out_dir)
    LOG.info("Headless: %r", args.headless)
    LOG.info("Max number of images to download: %d \n", args.max_count)

    LOG.info("Started extracting URLs")
    web_driver = get_driver(args.headless)
    links_dict = dict()
    with tqdm(obj_to_search, desc="Extracting URLs", colour="green") as progress_bar:
        for obj in progress_bar:
            img_links = extract_urls(web_driver=web_driver, obj=obj, max_urls=args.max_count)
            links_dict[obj] = img_links
        LOG.info("URL extract complete.")

    LOG.info("Starting download")

    for item in links_dict.items():
        download_images(
            item[1][: args.max_count], obj_to_search=item[0], out_dir=args.out_dir
        )

    LOG.info("Downloading complete.")
    web_driver.quit()


def main():
    """Parse arguments and start crawling."""
    parser = argparse.ArgumentParser(description="Image crawler")
    parser.add_argument(
        "--object",
        default="",
        type=str,
        required=True,
        help="Enter the object to search for.",
    )
    parser.add_argument(
        "--out_dir", default="./images", type=str, help="Destination path for images."
    )
    parser.add_argument("--headless", help="Runs in background.", action="store_true")
    parser.add_argument(
        "--max_count",
        default=DEFAULT_IMG_COUNT,
        help=f"Maximum number of images to download, defaults to {DEFAULT_IMG_COUNT}",
    )

    args = parser.parse_args()
    if not os.path.exists(args.out_dir):
        os.mkdir(args.out_dir)
    crawl(args)


if __name__ == "__main__":
    LOG = AppLogger().get_logger("image_crawler")
    main()
