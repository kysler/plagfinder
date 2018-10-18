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

def getText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return fullText

def googleSearch(uploaded_file):
    uploaded = getText(uploaded_file)
    text = ''.join(uploaded)
    sentences = tokenize.sent_tokenize(text)
    print(sentences)
    links = []
    for item in sentences:
        item = urllib.parse.quote_plus( item )
        url = 'https://google.com/search?q=' + item
        response = requests.get ( url )
        soup = BeautifulSoup(response.text, 'html.parser')
        links.append(soup.find('cite').text)
        results = list(OrderedDict.fromkeys(links))[0:5]
    return '[-]'.join(results)

def searchText(uploaded_file):
    text = uploaded_file
    sentences = tokenize.sent_tokenize(text)
    links = []
    for item in sentences:
        item = urllib.parse.quote_plus(item)
        url = 'https://google.com/search?q=' + item
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')    
        links.append(soup.find('cite').text)
        for x in links:
            print(x)
        results = list(OrderedDict.fromkeys(links))[0:5]
    return '[-]'.join(results)
