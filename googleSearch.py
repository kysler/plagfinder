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
from googlesearch import search
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



def searchText(uploaded_file):
    text = uploaded_file
    sentences = tokenize.sent_tokenize(text)
    links = []
    for item in sentences:
        for url in search(item, stop=1):
            links.append(url)
    results = list(OrderedDict.fromkeys(links))[0:5]
    return '[-]'.join(results)
