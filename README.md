# Introduction
These are suite of scripts to read data from rakuten and amazon order history.

# Chrome driver
```selenium``` needs Chrome driver. You usually download and install it into folder like ```C:\Users\amrul\programming\tool_downloads\chromedriver_win32```
and also add it to Windows ```Path```
And every time chrome is updated into a newer version, you will have to download newer version of chrome driver
from [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)

# How it works

You can install ```selenium``` with ```pip install```. The latest version I used was 4.3. 
You can find its documentations in https://www.selenium.dev/
In theory ```selenium``` allows you to control web browser the same way a human can do.
The only difference is that you will have to locate web elements by their names, tags.
Depending on the web page you are trying to control, this can sometimes be challenging.

First you import it and initialize it. Then you use its get method to start controlling a certain page

```python
from selenium import webdriver

driver = webdriver.Chrome()

driver.get("some url")
```

To access all buttons on a page

```python
from selenium.webdriver.common import By

buttons = driver.find_elements(By.TAG_NAME, "button")
```

Locate the button of choice and click on it

```python
login_buttons = [button for button in buttons if button.text=="Login"]
login_button = login_buttons[0]
login_button.click()
```

In below example we locate login and password inputs, enter text into them and press submit button
```python
rakuten_creds = get_rakuten_creds(pathlib.Path(r"C:\Users\amrul\PycharmProjects\jspanda_eshop_parsing\credentials"))
user_id = driver.find_element(By.NAME, "u")
user_id.send_keys(rakuten_creds["u"])
pasw = driver.find_element(By.NAME, "p")
pasw.send_keys(rakuten_creds["p"])
submit_btn = driver.find_element(By.NAME, "submit")
submit_btn.click()
```

Below demonstrates how you can locate links by their text and click on them
```python
order_hist_link = driver.find_element(By.LINK_TEXT, "購入履歴")
order_hist_link.click()
```

Below demonstrates how you can access elements by their class name
```python
order_list_items = driver.find_elements(By.CLASS_NAME, "oDrListItem")
```

# Parsing rakuten orders
You can find details of parsing rakuten order in [rakuten order parsing](docs/rakuten_orders_selenium_parsing.md)