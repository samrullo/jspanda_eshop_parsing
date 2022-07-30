import re
import datetime

from bs4 import BeautifulSoup


def find_elements_with_class(soup: BeautifulSoup, tag_name, class_name):
    return soup.find_all(tag_name, {'class': class_name})


def find_element_with_class(soup: BeautifulSoup, tag_name, class_name):
    return soup.find(tag_name, {'class': class_name})


def get_date_part_from_japanese_date(japanese_date, date_part):
    date_parts = re.findall("[0-9]+" + date_part, japanese_date)
    if len(date_parts) > 0:
        date_part = date_parts[0]
        date_numeric_parts = re.findall("[0-9]+", date_part)
        if len(date_numeric_parts) > 0:
            return int(date_numeric_parts[0])


def get_date_from_japanese_date(japanese_date):
    year = get_date_part_from_japanese_date(japanese_date, "年")
    month = get_date_part_from_japanese_date(japanese_date, "月")
    day = get_date_part_from_japanese_date(japanese_date, "日")
    return datetime.date(year, month, day)
