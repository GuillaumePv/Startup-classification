import nltk
import re
import pandas as pd
import numpy as np
from string import punctuation
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.utils import resample
import joblib


pd.set_option('display.max_columns', None)

# glove
glovebath = 'glove.6B.50d.txt'
with open(glovebath, 'r', encoding="utf8") as f:
    words = set()
    word2vector = {}
    for line in f:
        line_ = line.strip()
        words_Vec = line_.split()
        words.add(words_Vec[0])
        word2vector[words_Vec[0]] = list(map(float, words_Vec[1:]))


def load_data():
    df = pd.read_csv('train_data.csv', sep=',', header=0, encoding="ISO-8859-1")
    df = df.iloc[:, 1:4]
    df.columns = ['site', 'classification', 'text']
    df['classification'] = df['classification'].replace(['OPEN'], 'OTHER')
    df['classification'] = df['classification'].replace(['B2C/B2B'], 'B2C')
    df.loc[df["classification"] == "B2B", "classification"] = 0
    df.loc[df["classification"] == "B2C", "classification"] = 1
    df.loc[df["classification"] == "OTHER", "classification"] = 2
    B2B = df[df["classification"] == 0]
    B2C = df[df["classification"] == 1]
    OTHER = df[df["classification"] == 2]
    return B2B, B2C, OTHER

B2B, B2C, OTHER = load_data()

B2B_downsample = resample(B2B,
                          replace=True,
                          n_samples=len(OTHER),
                          random_state=42)

B2C_downsample = resample(B2C,
                          replace=True,
                          n_samples=len(OTHER),
                          random_state=42)
df = pd.concat([B2B_downsample, B2C_downsample, OTHER])

withoutpunc = []


def removepunc(text):
    result = ""
    for i in text:
        if i not in punctuation:
            result += i
    return result


def clean_numbers(x):
    if bool(re.search(r'\d', x)):
        x = re.sub('[0-9]{5,}', '#####', x)
        x = re.sub('[0-9]{4}', '####', x)
        x = re.sub('[0-9]{3}', '###', x)
        x = re.sub('[0-9]{2}', '##', x)
    return x


for i in range(len(df.loc[:, ['text']])):
    x = df.iloc[i]['text'].lower()
    withoutpunc.append([x])


def emmbedding(type, method):
    result = []
    wordsOfDoc = []
    for i in range(len(type)):
        # print(type[i])
        tmp = []
        for j in type[i]:
            # print(j)
            word = nltk.word_tokenize(j)
            wordsOfDoc.append(word)
            for p in word:
                if p in word2vector:
                    tmp.append(word2vector[p])
                else:
                    tmp.append([0] * 50)
            r = [sum(i) if method == "SUM" else sum(i) / len(i) for i in zip(*tmp)]
            result.append(r)
    return result


x = emmbedding(withoutpunc, 'SUM')

y = []
for i in range(len(df.loc[:, ['classification']])):
    y.append(df.iloc[i]['classification'])

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
model = RandomForestClassifier()



n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]

max_features = ['auto', 'sqrt']
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
max_depth.append(None)
min_samples_split = [2, 5, 10]
min_samples_leaf = [1, 2, 4]
bootstrap = [True, False]
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}


model_random = RandomizedSearchCV(estimator = model, param_distributions = random_grid, n_iter = 50, cv = 3, verbose=3, random_state=0, n_jobs = -1)
model_random.fit(X_train, y_train)
yPrediction = model_random.predict(X_test)
print(classification_report(y_test, yPrediction))
print(confusion_matrix(y_test, yPrediction))

filename = 'model/RFword2vec_model.sav'
joblib.dump(model_random, open(filename, 'wb'))