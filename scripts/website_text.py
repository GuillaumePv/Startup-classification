import os
from os import listdir
from path import path_data_github, path_data, path_data_html
import codecs
from bs4 import BeautifulSoup
import re

files = [f for f in listdir(path_data_html)][:10]
# print(files)
file = files[5]
print(file)

def clean_page_text(text):
    try:
        text= re.sub(r"[\s,:#][\.\-@]?[\d\w]+[\.\-@][\d\w\.\-@_]*"," ",text)
        text= re.sub(r"[\s,:][\.\-@][\d\w]+"," ",text)
        text= re.sub(r"\s\d[\d\w]+"," ",text)
        text= re.sub(r"[{}>\*/\';]"," ",text)
        text= re.sub(r"\s+"," ",text)
        text= re.sub(r"DOMContentLoaded.*_static"," ",text)

        #remove all these random unicode words
        #text = re.sub(r"(\W|^)\w*" + '\x00' + "\w*\W"," ",text)
        #text = re.sub(r"(\W|^)\w*" + '\x01' + "\w*\W"," ",text)
        #text= re.sub(r"(\W|^)\w*" + '\x03' + "\w*\W"," ",text)
        return text
    except MemoryError as e:
        print("Memory error !!!")
try:
    f=codecs.open(path_data_html+file, 'r', 'utf-8')
    soup = BeautifulSoup(f.read(), features="html.parser")
    text = soup.get_text(separator = ' ')
    print(text)
    new_text = clean_page_text(text) # bof le cleaning

    print("=== Text cleaned ===\n")
    print(new_text)


except MemoryError as e:
    print("Memory error !!!")



