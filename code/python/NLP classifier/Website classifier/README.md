# B2C/B2B Classifier

## Data

- HTML page scrapped during february 2022
- Using requests & BeautifulSoup libraries
- Delete duplicated, non-english html page
- scrapped based on the guzman paper

## Model

#1 label some random row from unlabelled data by hand -> training data

#2 import training data, downsample (B2B is over distributed)

#3 load pretrain word vectors word2vec (download 6B before )
https://nlp.stanford.edu/projects/glove/

#4 corpus embedding

#5 create, hyper parameter tuning model

#6 check performance, if good save model in order to use it to predict

#7 predict to new rows