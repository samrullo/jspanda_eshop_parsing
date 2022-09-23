import datetime
import re
import logging


def to_yyyymmdd(adate):
    return datetime.datetime.strftime(adate, "%Y%m%d")


def extract_date_token(adate_str, date_token):
    token_patterns = re.findall(f"[0-9]+{date_token}", adate_str)
    token_str = token_patterns[0]
    token_numb = token_str.replace(date_token, "")
    return int(token_numb)


def convert_japanese_date_string_to_date(adate_str):
    year = extract_date_token(adate_str, "年")
    month = extract_date_token(adate_str, "月")
    day = extract_date_token(adate_str, "日")
    logging.info(f"year : {year}, month : {month}, day : {day}")
    return datetime.date(year, month, day)