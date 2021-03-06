import urllib
from nltk import tokenize
from bs4 import BeautifulSoup
from collections import OrderedDict
import requests
import glob
import subprocess as sp
import os
import ctypes
import docx
import re
import webbrowser
import time
from itertools import chain

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

def searchText(uploaded_file):
    text = uploaded_file
    sentences = tokenize.sent_tokenize(text)
    links = []
    print(sentences)
    for item in sentences:
        keyword = urllib.parse.quote_plus(item)
        google_url = 'https://www.google.com/search?q={}&num={}'.format(keyword, 5)
        r = requests.get(google_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        url = soup.select('.r a')
        if url:
            urlclean = url[0]['href']
            links.append(urlclean)
        time.sleep(3)
    results = list(OrderedDict.fromkeys(links))[0:5]
    return '[-]'.join(results)
