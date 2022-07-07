from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize 

# Uncomment here to download the latest nltk stop words
import nltk
from nltk.corpus import stopwords
import numpy as np

import pandas as pd
## add functions inside utils
import os
import sys
#adding directory to path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)

sys.path.append(parentdir+"/utils/")
from path import path_data_github, path_data, path_data_html

df = pd.read_csv(path_data+"website_info.csv")

invalid_condition = [
    df.text.str.contains("Internal Server")
    ]

df.at[np.any(invalid_condition, axis=0), 'is_valid_website'] = False
df.text = df.text.str.strip()
print(df.head(5))
