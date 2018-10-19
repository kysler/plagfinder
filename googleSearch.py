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
        item = urllib.parse.quote_plus(item)
        url = google_url = 'https://www.google.com/search?q={}&num={}'.format(item, 1)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')   
        result_block = soup.find_all('div', attrs={'class': 'g'})
        for result in result_block:
            link = result.find('a', href=True)
            title = result.find('h3', attrs={'class': 'r'})
            if link and title:
                link = link['href']
                title = title.get_text()
                if link != '#':
                    links.append(link)
    results = list(OrderedDict.fromkeys(links))[0:5]
    return '[-]'.join(results)



def searchText(uploaded_file):
    text = uploaded_file
    sentences = tokenize.sent_tokenize(text)
    links = []
    for item in sentences:
        item = urllib.parse.quote_plus(item)
        url = google_url = 'https://www.google.com/search?q={}&num={}'.format(item, 1)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')   
        result_block = soup.find_all('div', attrs={'class': 'g'})
        for result in result_block:
            link = result.find('a', href=True)
            title = result.find('h3', attrs={'class': 'r'})
            if link and title:
                link = link['href']
                title = title.get_text()
                    if link != '#':
                        links.append(link)
    results = list(OrderedDict.fromkeys(links))[0:5]
    return '[-]'.join(results)
