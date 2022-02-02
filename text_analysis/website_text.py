import os
from bs4 import BeautifulSoup
import sys
import pdb
import os
import re
import mimetypes
import re


def clean_page_text(text):
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