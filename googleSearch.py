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

def getText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return fullText

def googleSearch(uploaded_file):
    text = uploaded_file
    sentences = tokenize.sent_tokenize(text)
    links = []
    for item in sentences:
        for url in search(item, stop=1):
            links.append(url)
    results = list(OrderedDict.fromkeys(links))[0:5]
    return '[-]'.join(results)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

def searchText(uploaded_file):
    text = uploaded_file
    sentences = tokenize.sent_tokenize(text)
    links = []
    for item in sentences:
        keyword = urllib.parse.quote_plus(item)
        google_url = 'https://www.google.com/search?q={}&num={}'.format(keyword, 1)
        r = requests.get(google_url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        url = soup.select('.r a')
        urlclean = url[0]['href']
        links.append(urlclean)
        time.sleep(3)
    results = list(OrderedDict.fromkeys(links))[0:5]
    return '[-]'.join(results)
