# NLP librairies
import spacy
spacy.load("en_core_web_sm")
from spacy.lang.en import English
parser = English()

from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer

import nltk
nltk.download('stopwords')
en_stop = set(nltk.corpus.stopwords.words('english'))

from website_text_dataset import website_text_dataset

def prepare_text_for_lda(self, text):
    tokens = self.tokenize(text)
    tokens = [token for token in tokens if len(token) > 4]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [self.get_lemma(token) for token in tokens]
    return tokens
        
def tokenize(self, text: str):
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        elif token.orth_.startswith('@'):
            lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens

def get_lemma(self, word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma
    

def get_lemma2(self,word):
    return WordNetLemmatizer().lemmatize(word)



website_text = website_text_dataset()
website_text.website_info = website_text.prep(website_text.website_info)
idx = website_text_dataset.get_valid_index(website_text.website_info)
website_text_cleaned = website_text.website_info.loc[idx]

text_data = []
for text in website_text_cleaned['text'][:3]:
    tokens = prepare_text_for_lda(text)
    text_data.append(tokens)

print(text_data)