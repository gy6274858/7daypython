from bs4 import BeautifulSoup
from lxml import etree
import requests
import os
import json
import os
url = 'https://bbs.hupu.com/33205110_115502915043979.html'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
response = requests.get(url, headers=headers)
# print(response.text)
html = etree.HTML(response.text)
img_list = html.xpath('//*[@id="tpc"]/div/div[2]/table[1]/tbody/tr/td/div[2]/div[2]')
for imgg in img_list:
    imgg = str(imgg)
    with open('./1.html','a') as file:
        file.write(imgg)