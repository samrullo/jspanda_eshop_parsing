import requests
from bs4 import BeautifulSoup

page = 1
url = f"https://order.my.rakuten.co.jp/?page=myorder&act=list&page_num={page}"
s = requests.Session()
data = {'u': 'subhonjon@yahoo.com', 'p': '18Aranid'}
res = s.post(url, data)
html = res.text
soup = BeautifulSoup(html, "lxml")
links = soup.find_all('a')
print(links)
print(f"there are total of {len(links)}")

itemwraps = soup.find_all('div', {'class': 'itemWrap'})
itemwrap = itemwraps[0]
itemname = itemwrap.find('li', {'class': 'itemName'})
print(f"Item name :{itemname.get_text().strip()}\n")
itemprice = itemwrap.find('li', {'class': 'itemPrice'})
itempricespan = itemprice.find('span', {'class': 'price'})
print(f"Item price : {itempricespan.get_text()}\n")

itemimgp = itemwrap.find('p', {'class': 'itemImg'})
itemimg = itemimgp.find('img')
itemimgurl = itemimg.attrs['src']
print(f"Item img url : {itemimgurl}")

with open("fino.jpg", "wb") as fh:
    fh.write(requests.get(itemimgurl).content)
