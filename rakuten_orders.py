import os
import json

import pandas as pd

from rakuten_order_parsing_utils import RakutenOrder, get_orders_url, get_order_item_wraps, get_order_list_items, \
    get_orders_url_soup, get_rakuten_session
import logging
from logging_utils.init_logging import init_logging

init_logging()

page = 1
orders_url = get_orders_url(page)
rakuten_session = get_rakuten_session(orders_url)
rakuten_orders = []
while True:
    orders_url = get_orders_url(page)
    soup = get_orders_url_soup(orders_url, rakuten_session)
    order_elements = get_order_list_items(soup)
    if len(order_elements) > 0:
        for idx, order_element in enumerate(order_elements):
            rakuten_order = RakutenOrder(order_element)
            rakuten_orders.append(rakuten_order)
            logging.info(f"page {page} | order {idx + 1} : {rakuten_order}")
    else:
        break
    page += 1
    if page > 30:
        break

logging.info(f"retrieved total of {len(rakuten_orders)}")
logging.info("next will store them into json file")
orders_file = "rakuten_orders.json"
with open(os.path.join("./data", "rakuten_orders.json"), "w") as fh:
    for order in rakuten_orders:
        fh.write(json.dumps(order.to_dict(), default=str))
logging.info(f"finished writing into {orders_file}")

logging.info("next will convert to dataframe")
orders_df_list = []
for order in rakuten_orders:
    orders_df_list.append(order.to_dataframe())
rakuten_orders_df = pd.concat(orders_df_list)
rakuten_orders_df.to_csv(os.path.join("./data", "rakuten_orders.csv"))
logging.info(f"rakuten orders dataframe size : {len(rakuten_orders_df)}")
