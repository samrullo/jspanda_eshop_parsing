import pathlib
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from rakuten_selenium_parsing_utils import get_rakuten_creds, extract_order_name_and_link
from date_utils import to_yyyymmdd, convert_japanese_date_string_to_date
from collections import namedtuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s %(lineno)s]')

# initialize selenium driver to control the rakuten web page
rakuten_ichiba_url = "https://www.rakuten.co.jp/"
driver = webdriver.Chrome()

# access rakuten top page
driver.get(rakuten_ichiba_url)
time.sleep(3)

# find login button and click on it
buttons = driver.find_elements(By.TAG_NAME, "button")
login_buttons = [button for button in buttons if button.text == 'ログイン']
logging.info(f"there are {len(login_buttons)} login buttons")
login_button = login_buttons[0]
login_button.click()

# fill in username and password and press submit
rakuten_creds = get_rakuten_creds(pathlib.Path(r"C:\Users\amrul\PycharmProjects\jspanda_eshop_parsing\credentials"),
                                  creds_file_name="rakuten_credentials.pkl")
user_id = driver.find_element(By.NAME, "u")
user_id.send_keys(rakuten_creds["u"])
pasw = driver.find_element(By.NAME, "p")
pasw.send_keys(rakuten_creds["p"])
submit_btn = driver.find_element(By.NAME, "submit")
submit_btn.click()

# find order history link and click on it, which will take us to orders history page
order_hist_link = driver.find_element(By.LINK_TEXT, "購入履歴")
order_hist_link.click()

# define a named tuple to hold an order item record
RakutenOrderItem = namedtuple("RakutenOrderItem", "order_id adate image name item_link price quantity total")

# the list which holds dataframes of orders from each page that we will eventually concatenate into one dataframe
rakuten_order_df_list = []

start_page = 1
end_page = 2
for page in range(start_page, end_page):
    logging.info(f"WILL PARSE PAGE {page}")
    rakuten_orders_url = f"https://order.my.rakuten.co.jp/?page=myorder&act=list&page_num={page}"
    driver.get(rakuten_orders_url)

    rakuten_order_items = []

    order_list_items = driver.find_elements(By.CLASS_NAME, "oDrListItem")
    logging.info(f"there are {len(order_list_items)} order_list_items")
    for order_list_item in order_list_items:
        purchase_date_el = order_list_item.find_element(By.CLASS_NAME, "purchaseDate")
        order_id_el = order_list_item.find_element(By.CLASS_NAME, "idNum")
        logging.info(f"Found purchase_date {purchase_date_el.text} and order id {order_id_el.text}")
        order_item_elements = order_list_item.find_elements(By.CLASS_NAME, "oDrListItemRightCont")
        for order_item_el in order_item_elements:
            image_el = order_item_el.find_element(By.TAG_NAME, "img")
            image_src = image_el.get_attribute("src")
            order_item_link, order_item_name = extract_order_name_and_link(order_item_el)
            price_el = order_item_el.find_element(By.CLASS_NAME, "price")
            price = int(price_el.text.replace(",", ""))
            quantity_el = order_item_el.find_element(By.CLASS_NAME, "itemNum")
            quantity_patterns = re.findall("[0-9]", quantity_el.text)
            quantity = int(quantity_patterns[0])
            order_item = RakutenOrderItem(order_id_el.text,
                                          purchase_date_el.text,
                                          image_src,
                                          order_item_name,
                                          order_item_link,
                                          price,
                                          quantity,
                                          price * quantity)
            logging.info(f"order item : {order_item}")
            rakuten_order_items.append(order_item)
    rakuten_order_df = pd.DataFrame(rakuten_order_items)
    logging.info(f"rakuten_order_df : {len(rakuten_order_df)}")
    rakuten_order_df_list.append(rakuten_order_df)

rakuten_orders_df = pd.concat(rakuten_order_df_list)
rakuten_orders_df.index = range(len(rakuten_orders_df))
logging.info(f"extracted total of {len(rakuten_orders_df)} rakuten orders")

rakuten_orders_df["purchase_date"] = rakuten_orders_df["adate"].apply(convert_japanese_date_string_to_date)
rakuten_orders_df["year"] = rakuten_orders_df["purchase_date"].map(lambda adate: adate.year)
rakuten_orders_df["month"] = rakuten_orders_df["purchase_date"].map(lambda adate: adate.month)
min_date = rakuten_orders_df["purchase_date"].min()
max_date = rakuten_orders_df["purchase_date"].max()

data_folder = pathlib.Path(r"C:\Users\amrul\PycharmProjects\jspanda_eshop_parsing\data")
file = f"rakuten_orders_{to_yyyymmdd(min_date)}_to_{to_yyyymmdd(max_date)}.xlsx"
rakuten_orders_df.to_excel(data_folder / file)
