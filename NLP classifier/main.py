import nltk
import re
import pandas as pd
from string import punctuation
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.utils import resample

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

    B2B = df[df["classification"] == "B2B"]
    B2C = df[df["classification"] == "B2C"]
    OTHER = df[df["classification"] == "OTHER"]
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
    x = removepunc(df.iloc[i]['text'])
    x = clean_numbers(df.iloc[i]['text'])
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
model = RandomForestClassifier(n_estimators=50, criterion='entropy', random_state=42)
model.fit(X_train, y_train)
yPrediction = model.predict(X_test)
print(accuracy_score(y_test, yPrediction) * 100)
