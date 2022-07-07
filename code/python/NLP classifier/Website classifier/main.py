import nltk
nltk.download('punkt')
from nltk.corpus import stopwords
words = stopwords.words("english")

import re
import pandas as pd
import numpy as np
from string import punctuation
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.utils import resample
from sklearn import metrics
import joblib
from tqdm import tqdm

# librairies for graphs and analysis of results
import matplotlib.pyplot as plt
import seaborn as sns
# create a condtion pour que ça soit utiliser en dehors de la VM
from wordcloud import WordCloud

pd.set_option('display.max_columns', None)

glovebath = 'glove.6B.50d.txt'
# glove
try:
    with open(glovebath, 'r', encoding="utf8") as f:
        words = set()
        word2vector = {}
        for line in f:
            line_ = line.strip()
            words_Vec = line_.split()
            words.add(words_Vec[0])
            word2vector[words_Vec[0]] = list(map(float, words_Vec[1:]))
except FileNotFoundError:
    print("You need to download glove.6B.50d.txt on http://nlp.stanford.edu/data/glove.6B.zip.")
    print("And put glove.6B.50d.txt on the folder NLP Classifier.")


def load_data():
    df = pd.read_csv('./NLP classifier/train_data.csv', sep=',', header=0, encoding="ISO-8859-1")
    df = df.iloc[:, 1:4]
    df.columns = ['site', 'classification', 'text']
    df['classification'] = df['classification'].replace(['OPEN'], 'OTHER')
    df['classification'] = df['classification'].replace(['B2C/B2B'], 'B2C')
    by_label = df.groupby("classification")
    text_by_label = by_label["text"].apply(lambda x: ",".join(x))
    word_clouds = {}
    for i, text in text_by_label.iteritems():
        if i.strip() != "":
            word_cloud = WordCloud(stopwords={"https", "ID", "github", "use"}.union(words),
                                collocations=False,
                                background_color="white",
                                max_font_size=60)
            word_clouds[i] = word_cloud.generate(text)

    for label, cloud in word_clouds.items():
        print(label)
        fixed = re.sub("/", "_", label)
        label = label.replace("/","_")
        cloud.to_image().save("./NLP classifier/graphs/" + label.lower() + "_cloud.png")

    df.loc[df["classification"] == "B2B", "classification"] = 0
    df.loc[df["classification"] == "B2C", "classification"] = 1
    df.loc[df["classification"] == "OTHER", "classification"] = 2
    B2B = df[df["classification"] == 0]
    B2C = df[df["classification"] == 1]
    OTHER = df[df["classification"] == 2]
    
    return B2B, B2C, OTHER

B2B, B2C, OTHER = load_data()

df_before = pd.concat([B2B, B2C, OTHER])
fig, ax = plt.subplots()
fig.suptitle("classification", fontsize=12)
df_before["classification"].reset_index().groupby("classification").count().sort_values(by= 
       "index").plot(kind="barh", legend=False, 
        ax=ax).grid(axis='x')
plt.savefig('./graphs/sampling_before_subsample.png')
plt.close()

B2B_downsample = resample(B2B,
                          replace=True,
                          n_samples=len(OTHER),
                          random_state=42)

B2C_downsample = resample(B2C,
                          replace=True,
                          n_samples=len(OTHER),
                          random_state=42)
df = pd.concat([B2B_downsample, B2C_downsample, OTHER])

fig, ax = plt.subplots()
fig.suptitle("classification", fontsize=12)
df["classification"].reset_index().groupby("classification").count().sort_values(by= 
       "index").plot(kind="barh", legend=False, 
        ax=ax).grid(axis='x')
plt.savefig('./graphs/sampling_after_subsample.png')
plt.close()

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

print("=== beging embedding ===")
def emmbedding(type, method):
    result = []
    wordsOfDoc = []
    for i in tqdm(range(len(type))):
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
y_score = model_random.predict_proba(X_test)
filename = 'model/RFword2vec_model.sav'
joblib.dump(model_random, open(filename, 'wb'))

classes = np.unique(y_test)
y_test_array = pd.get_dummies(y_test, drop_first=False).values
    
## Accuracy, Precision, Recall
accuracy = metrics.accuracy_score(y_test, yPrediction)
print("Accuracy:",  round(accuracy,2))

print("Detail:")
print(metrics.classification_report(y_test, yPrediction))
    
## Plot confusion matrix
cm = metrics.confusion_matrix(y_test, yPrediction)
fig, ax = plt.subplots()
sns.heatmap(cm, annot=True, fmt='d', ax=ax, cmap=plt.cm.Blues, 
            cbar=False)
ax.set(xlabel="Pred", ylabel="True", xticklabels=classes, 
       yticklabels=classes, title="Confusion matrix")
plt.yticks(rotation=0)
plt.savefig('./graphs/confusion_matrix.png')
plt.close()
fig, ax = plt.subplots(nrows=1, ncols=2)
## Plot roc
for i in range(len(classes)):
    fpr, tpr, thresholds = metrics.roc_curve(y_test_array[:,i],  
                           y_score[:,i])
    ax[0].plot(fpr, tpr, lw=3, 
              label='{0} (area={1:0.2f})'.format(classes[i], 
                              metrics.auc(fpr, tpr))
               )
ax[0].plot([0,1], [0,1], color='navy', lw=3, linestyle='--')
ax[0].set(xlim=[-0.05,1.0], ylim=[0.0,1.05], 
          xlabel='False Positive Rate', 
          ylabel="True Positive Rate (Recall)", 
          title="Receiver operating characteristic")
ax[0].legend(loc="lower right")
ax[0].grid(True)
    
## Plot precision-recall curve
for i in range(len(classes)):
    precision, recall, thresholds = metrics.precision_recall_curve(y_test_array[:,i], y_score[:,i])
    ax[1].plot(recall, precision, lw=3, 
               label='{0} (area={1:0.2f})'.format(classes[i], 
                                  metrics.auc(recall, precision))
              )
ax[1].set(xlim=[0.0,1.05], ylim=[0.0,1.05], xlabel='Recall', 
          ylabel="Precision", title="Precision-Recall curve")
ax[1].legend(loc="best")
ax[1].grid(True)
plt.tight_layout()
plt.savefig('./graphs/roc_curve_and_precision_recall_curve.png')
plt.close()