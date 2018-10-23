import glob
import subprocess as sp
import os
import ctypes
import docx
from nltk import tokenize
from fuzzywuzzy import fuzz, process
import nltk

#Function to call Cosine Similarity to gather results.
def similar(a, b):
    return fuzz.partial_ratio(a,b)

#Extracts text from .docx file
def getText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return fullText

#Main Plagiarism Scanner Function
#Main Plagiarism Scanner Function
def scan(textfile):
    data = tokenize.sent_tokenize(textfile)
    doclist = []
    copiedlist = []
    counter = 0
    avg = 0
    total_ratio = 0
    for filename in glob.glob("files/*.docx"):
        data2 = tokenize.sent_tokenize(getText(filename))
        ratio = round(similar(data, data2), 2)
        doc_name = filename.split('\\')[-1].split('.')[0]
        if(ratio >= 40):
            doclist.append(doc_name)
            counter += 1
            total_ratio += ratio
            for item in data:
                copiedline = process.extractOne(item, data2)
                stringedline = copiedline[0]
                copiedlist.append(stringedline)
    avg = round(total_ratio/counter, 2)
    return doclist, copiedlist
