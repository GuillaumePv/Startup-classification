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

data = data_reader()
class WebsiteText:

    def __init__(self):
        self.dirs = data.scrapped_website

    def create_website_text(self):
        if os.path.isfile(path_data+"wesbite_not_working.txt"):
            os.remove(path_data+"wesbite_not_working.txt")
        else:
            f = open(path_data+"wesbite_not_working.txt","w", encoding="utf-8")
            f.close()
        try:

            documents = []
            startups = []
            lang = []
            error = 0
            no_file = 0
            no_en = 0
            for dir in tqdm(self.dirs[:]):
                list_file = os.listdir(path_data_html+dir)
                if len(list_file) > 0:
                    try:
                        f = codecs.open(path_data_html+dir+f'/{list_file[0]}', 'r', 'utf-8')
                        soup = BeautifulSoup(f.read(), features="html.parser")
                        text = soup.get_text(separator=' ')
                        clean_text = self.clean_page_text(text)  # bof le cleaning
                        documents.append(clean_text)
                        startups.append(str(list_file[0]).split(".html")[0])

                    except UnicodeDecodeError:
                        error += 1
                        f = open(path_data+"wesbite_not_working.txt","a",encoding="utf-8")
                        f.write(dir+", UnicodeDecodeError"+"\n")
                        f.close()
                    
                    except PermissionError:
                        error += 1
                        f = open(path_data+"wesbite_not_working.txt","a",encoding="utf-8")
                        f.write(dir+", PermissionError"+"\n")
                        f.close()
                else:
                    no_file += 1
                    f = open(path_data+"wesbite_not_working.txt","a",encoding="utf-8")
                    f.write(dir+", no_file"+"\n")
                    f.close()
            data = {"website": startups, "text": documents}

            df = pd.DataFrame(data)
            df.to_csv(f'{path_data}/website_info.csv', index=False)
            print(f"number of errors: {error}")
            print(f"number of not working website: {no_file}")

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
    website_text = WebsiteText()
    website_text.create_website_text()
