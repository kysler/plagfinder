import glob
import subprocess as sp
import os
import ctypes
import docx
from fuzzywuzzy import fuzz, process
import nltk

#Function to call Cosine Similarity to gather results.
def similar(a, b):
    return fuzz.partial_token_sort_ratio(a,b)

#Function to remove all files in upload folder
def removefiles():
    path = 'tmp/uploads'
    for file in os.scandir ( path ):
        if file.name.endswith ( ".docx" ):
            os.unlink ( file.path )

#Extracts text from .docx file
def getText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return fullText

#Main Plagiarism Scanner Function
def plagscan(uploaded_file):
    result = open('result.log', "w")
    result.writelines("")
    result.close

    try:
        data = [ getText(uploaded_file) ]
        counter = 0
        fullOutput = [ ]
        fullOutput2 = [ ]
        for filename in glob.glob("files/*.docx"):
            data2 = [ getText ( filename ) ]
            counter += 1
            ratio = round(similar(data, data2), 2)
            doc_name = filename.split('\\')[-1].split('.')[0]
            resultText = "Plagiarised Content Found in "+ filename.split('\\')[-1].split('.')[0] + " Results " + " || " + ratio.__str__()+"%" + '\n\n'

            if(ratio >= 30):
                fullOutput.append(doc_name)
                fullOutput2.append(resultText)

                for item in data:
                    str1 = item.__str__()
                    copied_line = process.extractOne ( str1, data2 )
                    copied_list = copied_line.__str__()

                str3 = ''.join ( copied_list ) + '\n'
                fullOutput2.append(str3)
                str4 = ''.join (fullOutput2)
                result = open ( 'tmp/result.log', "w", encoding='utf-8' )
                result.write ( str4 )

    except docx.opc.exceptions.PackageNotFoundError:
        ctypes.windll.user32.MessageBoxW(0, "It's not a docx file!", "Not docx file!", 0)

    #THROWS THE OUTPUT TO MAIN FLASK PROGRAM
    return fullOutput
