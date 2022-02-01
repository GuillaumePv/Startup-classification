import os
from os import listdir
from path import path_data_github, path_data, path_data_html
import codecs
from bs4 import BeautifulSoup
import re
import pandas as pd
from tqdm import tqdm
from langdetect import detect, LangDetectException
files = [f for f in listdir(path_data_html)][:]
# print(files)
file = files[5]
print(file)


class website_text:
    """
    (in construction)
    class to create analysis of html page
    """
    def __init__(self, path):
        self.texts = self.load_domain(path)
        print("creation class website")

    def load_domain(self,path):
        path_file = path

        return path_file


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

def detect_lang(text):
    try:
        lang = detect(text)
        if lang != "en":
            return False
        else:
            return True
    except LangDetectException:
        return False

try:

    documents = []
    startups = []

    error = 0
    no_en = 0
    for file in tqdm(files):
        try:
            f=codecs.open(path_data_html+file, 'r', 'utf-8')
            soup = BeautifulSoup(f.read(), features="html.parser")
            text = soup.get_text(separator = ' ')
            clean_text = clean_page_text(text) # bof le cleaning
            is_en = detect_lang(clean_text)
            # print("=== Text cleaned ===\n")
            
            if is_en:
                documents.append(clean_text)
                startups.append(str(file).split(".html")[0])
            else:
                no_en += 1
            # print(str(file).split(".html")[0])
        
        except UnicodeDecodeError:
            error += 1

    data = {
        "startup":startups,
        "text":documents
    }

    df = pd.DataFrame(data)
    df.to_csv(f'{path_data}/website_info.csv',index=False)
    print(f"number of errors: {error}")
    print((f"page no english: {no_en}"))


except MemoryError as e:
    print("Memory error !!!")



