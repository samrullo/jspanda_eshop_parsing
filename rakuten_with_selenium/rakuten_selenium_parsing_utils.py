import os
import pathlib
import pickle
import selenium
from selenium.webdriver.common.by import By


def get_rakuten_creds(folder: pathlib.Path):
    cred_folder = folder
    creds_file = "rakuten_credentials.pkl"
    with open(os.path.join(cred_folder, creds_file), "rb") as fh:
        creds = pickle.load(fh)
        return creds


def extract_order_name_and_link(order_item: selenium.webdriver.remote.webelement.WebElement):
    """
    Extract order name and ordered item url from order div item
    :param order_item:
    :return: a tuple of order item url and order item name
    """
    item_links = order_item.find_elements(By.TAG_NAME, "a")
    nonblank_item_links = [item for item in item_links if item.text.strip() != ""]
    item_link = nonblank_item_links[0]
    return (item_link.get_attribute("href"), item_link.text)
