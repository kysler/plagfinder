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
        item = urllib.parse.quote_plus(item)
        url = "https://google.com/search?q=" + item
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        get_details = soup.find_all("div", attrs={"class": "g"})
        final_data = []
        for details in get_details:
            link = details.find_all("h3")
            # links = ""
            for mdetails in link:
                links = mdetails.find_all("a")
                lmk = ""
                for lnk in links:
                    lmk = lnk.get("href")[7:].split("&")
                    sublist = []
                    sublist.append(lmk[0])
                links.append = [sublist]
        results = list(OrderedDict.fromkeys(links))[0:5]
    return '[-]'.join(results)


def searchText(uploaded_file):
    text = uploaded_file
    sentences = tokenize.sent_tokenize(text)
    links = []
    for item in sentences:
        item = urllib.parse.quote_plus(item)
        url = "https://google.com/search?q=" + item
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        get_details = soup.find_all("div", attrs={"class": "g"})
        final_data = []
        for details in get_details:
            link = details.find_all("h3")
            # links = ""
            for mdetails in link:
                links = mdetails.find_all("a")
                lmk = ""
                for lnk in links:
                    lmk = lnk.get("href")[7:].split("&")
                    sublist = []
                    sublist.append(lmk[0])
                links.append = [sublist]
        results = list(OrderedDict.fromkeys(links))[0:5]
    return '[-]'.join(results)
