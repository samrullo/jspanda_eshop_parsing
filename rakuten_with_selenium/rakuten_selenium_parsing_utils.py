import os
import pathlib
import pickle
import selenium
from selenium.webdriver.common.by import By


def get_rakuten_creds(creds_folder: pathlib.Path, creds_file_name: str = "rakuten_credentials.pkl"):
    cred_folder = creds_folder
    creds_file = creds_file_name
    with open(cred_folder/creds_file, "rb") as fh:
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
