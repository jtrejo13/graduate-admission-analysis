# @Author: Juan Trejo
# @Date:   2018-03-28T15:23:05-05:00
# @Last modified by:   jtrj13
# @Last modified time: 2018-05-02T13:03:10-05:00


import requests
from bs4 import BeautifulSoup as soup

url_generic = 'https://thegradcafe.com/survey/index.php?q=computer+science%2A&t=a&pp=250&o=d&p={0}'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) \
 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

for i in range(1, 147):
    url = url_generic.format(i)
    r = requests.get(url, headers=headers)
    html = r.text
    page = soup(html, 'html.parser')
    file_name = './raw_data/page_{page}.html'.format(page=i)
    with open(file_name, 'w') as f:
        f.write(r.text)
    print('reading page {page}...'.format(page=i))
