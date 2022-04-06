import nltk
import os
import numpy as np
import pandas as pd
from string import punctuation
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
#glove
glovebath = 'glove.6B.50d.txt'
with open(glovebath, 'r', encoding="utf8") as f:
        words = set()
        word2vector = {}
        for line in f:
            line_ = line.strip()
            words_Vec = line_.split()
            words.add(words_Vec[0])
            word2vector[words_Vec[0]] = list(map(float, words_Vec[1:]))

df = pd.read_csv('train_data.csv', sep=',', header=0, encoding = "ISO-8859-1")
df = df.iloc[:, 1:4]
df.columns = ['site', 'classification', 'text']


withoutpunc = []


def removepunc(text):
    result = ""
    for i in text:
        if i not in punctuation:
            result += i
    return result


for i in range(len(df.loc[:, ['text']])):
    x = removepunc(df.iloc[i]['text'])
    withoutpunc.append([x])


def emmbedding(type, method):
    result = []
    wordsOfDoc = []
    for i in range(len(type)):
        #print(type[i])
        tmp = []
        for j in type[i]:
            #print(j)
            word = nltk.word_tokenize(j)
            wordsOfDoc.append(word)
            for p in word:
                if p in word2vector:
                    tmp.append(word2vector[p])
                else:
                    tmp.append([0]*50)
            r = [sum(i) if method == "SUM" else sum(i)/len(i) for i in zip(*tmp)]
            result.append(r)
    return result


x = emmbedding(withoutpunc, 'SUM')


y = []
for i in range(len(df.loc[:, ['classification']])):
    y.append(df.iloc[i]['classification'])



X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
model = LogisticRegression(class_weight='balanced',multi_class='multinomial', C=1e7)
model.fit(X_train, y_train)
yPrediction = model.predict(X_test)
print(yPrediction)
acc = accuracy_score(y_test, yPrediction)
print(acc)
print(acc*100)