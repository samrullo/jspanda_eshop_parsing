import requests
from utils import find_elements_with_class, find_element_with_class, get_date_from_japanese_date
from bs4 import BeautifulSoup
import pickle
import os
import re
import pandas as pd


def get_rakuten_creds():
    cred_folder = r"/Users/samrullo/PycharmProjects/jspanda_eshop_parsing/credentials"
    creds_file = "rakuten_credentials.pkl"
    with open(os.path.join(cred_folder, creds_file), "rb") as fh:
        creds = pickle.load(fh)
        return creds


def get_orders_url(page):
    return f"https://order.my.rakuten.co.jp/?page=myorder&act=list&page_num={page}"


def get_rakuten_session(orders_url):
    s = requests.Session()
    s.post(orders_url, get_rakuten_creds())
    return s


def get_orders_url_soup(orders_url, _session):
    res = _session.get(orders_url)
    html = res.text
    soup = BeautifulSoup(html, "lxml")
    return soup


def get_order_item_wraps(soup):
    return find_elements_with_class(soup, "div", "itemWrap")


def get_order_list_items(soup):
    return find_elements_with_class(soup, "div", "oDrListItem clfx")


def get_order_left_grid(order_item):
    return find_element_with_class(order_item, "td", "leftGrid")


def get_order_right_grid(order_item):
    return find_element_with_class(order_item, "td", "rightGrid")


class RakutenOrder:
    def __init__(self, order_list_item):
        self.order_list_item = order_list_item
        self.order_left_grid = get_order_left_grid(self.order_list_item)
        self.order_id = self._get_order_id()
        self.order_date = self._get_order_date()
        self.order_items = []
        order_right_grid = get_order_right_grid(self.order_list_item)
        order_item_elements = get_order_item_wraps(order_right_grid)
        if len(order_item_elements) > 0:
            for order_item_element in order_item_elements:
                self.order_items.append(RakutenOrderItem(order_item_element))

    def to_dict(self):
        return {"order_id": self.order_id, "order_date": self.order_date,
                "order_items": [order_item.to_dict() for order_item in self.order_items]}

    def to_dataframe(self):
        df = pd.DataFrame(columns=["order_id", "order_date", "name", "price", "quantity", "image_url"],
                          data=[{"order_id": self.order_id, "order_date": self.order_date, **order_item.to_dict()} for
                                order_item in self.order_items])
        return df

    def __repr__(self):
        return f"Order Id : {self.order_id}, Order date : {self.order_date}, order_items: {len(self.order_items)}"

    def _get_order_id(self):
        order_id_li_element = find_element_with_class(self.order_left_grid, "li", "orderID")
        order_id_span_element = find_element_with_class(order_id_li_element, "span", "idNum")
        return order_id_span_element.get_text()

    def _get_order_date(self):
        order_date_li_element = find_element_with_class(self.order_left_grid, "li", "purchaseDate")
        return get_date_from_japanese_date(order_date_li_element.get_text())


class RakutenOrderItem:
    def __init__(self, order_item):
        self.order_item = order_item
        self.name = self._get_order_name()
        self.price = self._get_order_item_price()
        self.quantity = self._get_quantity()
        self.image_url = self._get_image_url()

    def to_dict(self):
        return {key: val for key, val in self.__dict__.items() if key != "order_item"}

    def _get_order_name(self):
        name_li_element = find_element_with_class(self.order_item, "li", "itemName")
        return name_li_element.get_text().strip()

    def _get_order_item_price(self):
        price_li_element = find_element_with_class(self.order_item, "li", "itemPrice")
        price_span_element = find_element_with_class(price_li_element, "span", "price")
        price_txt = price_span_element.get_text().replace(",", "")
        return int(price_txt)

    def _get_quantity(self):
        quantity_li_element = find_element_with_class(self.order_item, "li", "itemNum")
        quantity_number_txt_list = re.findall("[0-9]+", quantity_li_element.get_text())
        if len(quantity_number_txt_list) > 0:
            return int(quantity_number_txt_list[0])
        else:
            return 0

    def _get_image_url(self):
        img_p_element = find_element_with_class(self.order_item, "p", "itemImg")
        img_element = img_p_element.find("img")
        img_url = img_element.attrs['src']
        return img_url
