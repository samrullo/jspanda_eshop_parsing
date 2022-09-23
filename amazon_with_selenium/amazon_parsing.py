import pathlib
import os
import pickle
import time
import re
import datetime
import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from date_utils import to_yyyymmdd
# dinara201181@mail.ru

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s %(lineno)s]')


def extract_order_id_from_order_link(order_link):
    order_id_patterns = re.findall("orderID=.*", order_link)
    if len(order_id_patterns) > 0:
        order_id_pattern = order_id_patterns[0].split("=")[-1]
    else:
        order_id_pattern = "NO_ORDER_ID"
    return order_id_pattern


amazon_url = "https://www.amazon.co.jp/gp/your-account/order-history?opt=ab&digitalOrders=1&unifiedOrders=1&returnTo=&__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&orderFilter=year-2022"

# we will use two drivers
# one to parse list of orders
# another to parse order details
driver_main = webdriver.Chrome()
driver_od = webdriver.Chrome()

driver_main.get(amazon_url)
driver_od.get(amazon_url)
time.sleep(3)

cred_folder = pathlib.Path(r"C:\Users\amrul\PycharmProjects\jspanda_eshop_parsing\credentials")
cred_file = "amazon_credentials.pkl"
with open(cred_folder / cred_file, "rb") as fh:
    amazon_creds = pickle.load(fh)

for driver in (driver_main, driver_od):
    # enter email and click next
    email_el = driver.find_element(By.NAME, "email")
    email_el.send_keys(amazon_creds["username"])
    submit_el = driver.find_element(By.ID, "continue")
    submit_el.click()

    # enter password and click login
    pasw_el = driver.find_element(By.ID, "ap_password")
    pasw_el.send_keys(amazon_creds["password"])
    login_el = driver.find_element(By.ID, "signInSubmit")
    login_el.click()

from collections import namedtuple

AmazonOrderItem = namedtuple("AmazonOrderItem",
                             "order_link order_total_sum purchase_date image name price quantity total")

amazon_order_items = []

# find pagination bar so that we can navigate to each page
pagination_bar = driver_main.find_element(By.XPATH, "//div[@class='a-text-center pagination-full']")

start_page = 1
end_page = 36
for page in range(start_page, end_page):
    if page != 1:
        pagination_bar = driver_main.find_element(By.XPATH, "//div[@class='a-text-center pagination-full']")
    page_btn = pagination_bar.find_element(By.LINK_TEXT, str(page))
    page_btn.click()

    # save current page url for later use
    current_page_url = driver_main.current_url

    order_items = driver_main.find_elements(By.XPATH, "//div[@class='a-box a-color-offset-background order-info']")
    logging.info(f"there are {len(order_items)} on page {page}")

    for order_item in order_items:
        order_item_columns = order_item.find_elements(By.CLASS_NAME, "a-column")

        # extract purchase date
        purchase_date_column = order_item_columns[0]
        purchase_date_rows = purchase_date_column.find_elements(By.CLASS_NAME, "a-row")
        purchase_date_el = purchase_date_rows[1]
        purchase_date = purchase_date_el.text

        # extract total sum
        total_sum_column = order_item_columns[1]
        total_sum_rows = total_sum_column.find_elements(By.CLASS_NAME, "a-row")
        total_sum_el = total_sum_rows[1]
        order_total_sum = int(total_sum_el.text.strip().replace("￥", "").replace(",", ""))

        # extract order link
        order_link_el = order_item.find_element(By.LINK_TEXT, "View order details")
        order_link = order_link_el.get_attribute("href")

        # let's view order details and extract info
        driver_od.get(order_link)
        shipment_box_el = driver_od.find_element(By.CLASS_NAME, "shipment")
        order_details_box_el = shipment_box_el.find_element(By.XPATH,
                                                            "//div[@class='a-fixed-right-grid-col a-col-left']")
        order_details_box_el2 = order_details_box_el.find_element(By.CLASS_NAME, "a-row")
        order_details_item_elements = order_details_box_el2.find_elements(By.XPATH,
                                                                          "//div[@class='a-text-center a-fixed-left-grid-col a-col-left']")

        for order_detail_item in order_details_item_elements:
            product_image_el = order_detail_item.find_element(By.TAG_NAME, "img")
            product_image = product_image_el.get_attribute('src')

            product_desc_element = order_detail_item.find_element(By.XPATH,
                                                                  "//div[@class='a-fixed-left-grid-col yohtmlc-item a-col-right']")
            product_desc_rows = product_desc_element.find_elements(By.CLASS_NAME, "a-row")

            # extract product description
            product_description = product_desc_rows[0].text

            # extract price
            price_elements = [item.text for item in product_desc_rows if '￥' in item.text]
            price = int(price_elements[0].replace('￥', "").replace(",", ""))

            # extract quantity
            try:
                quantity_el = order_detail_item.find_element(By.CLASS_NAME, "item-view-qty")
                quantity = int(quantity_el.text.replace(",", ""))
            except Exception as e:
                quantity = 1

            total_sum = quantity * price
            amazon_order_item = AmazonOrderItem(order_link, order_total_sum, purchase_date, product_image,
                                                product_description, price, quantity, total_sum)
            amazon_order_items.append(amazon_order_item)
            logging.info(f"Added amazon order item : {amazon_order_item}")

            # let's go back to main page
            # driver_main.get(current_page_url)

amorders_df = pd.DataFrame(amazon_order_items)
amorders_df["pur_date_text"] = amorders_df["purchase_date"]
amorders_df["purchase_date"] = amorders_df["pur_date_text"].map(
    lambda adate: datetime.datetime.strptime(adate, "%B %d, %Y"))
amorders_df["order_id"] = amorders_df["order_link"].map(lambda order_link: extract_order_id_from_order_link(order_link))
logging.info(f"extracted total of {len(amorders_df)} amazon order items")

min_date = amorders_df["purchase_date"].min()
max_date = amorders_df["purchase_date"].max()
data_folder = pathlib.Path(r"C:\Users\amrul\PycharmProjects\jspanda_eshop_parsing\data")
file = f"amazon_orders_{to_yyyymmdd(min_date)}_to_{to_yyyymmdd(max_date)}.xlsx"
amorders_df.to_excel(data_folder / file)
