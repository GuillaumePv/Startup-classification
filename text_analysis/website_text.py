import os
from bs4 import BeautifulSoup
import sys
import pdb
import os
import re
import mimetypes
import re
from tqdm import tqdm
import codecs
import pandas as pd

import os
import sys
#adding directory to path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)

sys.path.append(parentdir+"/utils/")
from path import path_data, path_data_html

sys.path.append(parentdir+"/download/")
from data_reader import data_reader

class website_text:

    def __init__(self):
        self.files = data_reader.read_html_files()

    def create_website_text(self):
        try:

            documents = []
            startups = []
            lang = []
            error = 0
            no_en = 0
            for file in tqdm(self.files):
                try:
                    f = codecs.open(path_data_html + file, 'r', 'utf-8')
                    soup = BeautifulSoup(f.read(), features="html.parser")
                    text = soup.get_text(separator=' ')
                    clean_text = self.clean_page_text(text)  # bof le cleaning
                    documents.append(clean_text)
                    startups.append(str(file).split(".html")[0])

                except UnicodeDecodeError:
                    error += 1

            data = {"website": startups, "text": documents}

            df = pd.DataFrame(data)
            df.to_csv(f'{path_data}/website_info.csv', index=False)
            print(f"number of errors: {error}")

        except MemoryError as e:
            print("Memory error !!!")

    def clean_page_text(self,text):
        try:
            text = re.sub(r"[\s,:#][\.\-@]?[\d\w]+[\.\-@][\d\w\.\-@_]*", " ", text)
            text = re.sub(r"[\s,:][\.\-@][\d\w]+", " ", text)
            text = re.sub(r"\s\d[\d\w]+", " ", text)
            text = re.sub(r"[{}>\*/\';]", " ", text)
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"DOMContentLoaded.*_static", " ", text)

            #remove all these random unicode words
            #text = re.sub(r"(\W|^)\w*" + '\x00' + "\w*\W"," ",text)
            #text = re.sub(r"(\W|^)\w*" + '\x01' + "\w*\W"," ",text)
            #text= re.sub(r"(\W|^)\w*" + '\x03' + "\w*\W"," ",text)
            return text
        except MemoryError as e:
            print("Memory error !!!")


if __name__ == "__main__":
    print("main file")