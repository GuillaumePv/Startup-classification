#####################################################
# based on https://github.com/Komod0D/repo-classifier
#####################################################

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)

sys.path.append(parentdir+"/utils/")
from path import path_github_folder

import scipy.sparse
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import pickle
import gc


labels = ["API", "Blockchain", "Compliance", "Data/ML", "Development", "HR", "Infrastructure",
          "Monetization", "Productivity", "UI", "Security","Framework","Scalability"]

print("Loading labelled data")
labelled_df = pd.read_csv(path_github_folder + "external_repo_classification.csv")
labelled_df =  labelled_df.rename(columns={"repo_text":"text","type1":"label"})
print(labelled_df.shape)

labelled_df.dropna(axis=0, inplace=True, subset=["repo", "text"])
labelled_df = labelled_df.loc[~pd.isnull(labelled_df[['label']]).any(axis=1)]
print(labelled_df.shape)
labelled_df.reset_index(inplace=True, drop=True)

print({label: len(labelled_df[labelled_df["label"] == label]) for label in labels}) #150 classified website

print("Loading unlabelled data")
unlabelled_df = pd.read_csv(path_github_folder + "unclassified_new_github.csv")
unlabelled_df.dropna(axis=0, inplace=True, subset=["repo", "text"])
unlabelled_df.reset_index(drop=True, inplace=True)

print(len(unlabelled_df))
gc.collect()

print("Fitting CV & TFIDF")

corpus = labelled_df["text"].append(unlabelled_df["text"]).tolist()
eng = stopwords.words("english")

cv = CountVectorizer(stop_words=eng, min_df=0.01, max_df=0.1)
tfidf = TfidfTransformer()

print("Fitting CV")
labelled_corpus = labelled_df["text"].tolist()
unlabelled_corpus = unlabelled_df["text"].tolist()
cv.fit(corpus)

print("Fitting TFIDF")
arr = cv.transform(labelled_corpus)
arr = tfidf.fit_transform(arr)

print("Transforming")
unlabelled_arr = tfidf.transform(cv.transform(unlabelled_corpus))

print("Dimensionality Reduction")
n_components = 400
svd = TruncatedSVD(n_components=n_components, n_iter=20)
print("Fitting SVD")
svd.fit(scipy.sparse.vstack((arr, unlabelled_arr)))

explained_variance = np.sum(svd.explained_variance_ratio_)
print(f"Explained variance with {n_components} components: {explained_variance * 100}%")

with open("others.svd", "wb") as f:
    pickle.dump(svd, f)

## save svd model and load it
# svd for 100000 component
# with open("100000.svd", "rb") as f:
#     svd = pickle.load(f)

print("Generating Dataset")
X = svd.transform(arr)
Y = np.zeros(shape=(X.shape[0],))

for i, row in labelled_df.iterrows():
    label = row["label"]
    if not pd.isna(label):
        Y[i] = labels.index(label)

X_out = svd.transform(unlabelled_arr)
print("Shape X")
print(X.shape)

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=20)
classifier = KNeighborsClassifier(n_neighbors=5, weights="distance")
classifier.fit(X_train, Y_train)
Y_pred = classifier.predict(X_test)
print(accuracy_score(Y_test, Y_pred))

plt.hist(Y)
plt.show()

print("Predicting")
knn = KNeighborsClassifier(n_neighbors=5, weights="distance")
knn.fit(X, Y)

Y_proba = knn.predict_proba(X_out)
Y_pred = np.argmax(Y_proba, axis=1)
Y_conf = np.max(Y_proba, axis=1)

threshold = 0.401
selection = Y_conf < threshold
n_low_confidence = np.count_nonzero(selection) / len(Y_conf)
print(f"{n_low_confidence * 100}% \"low\" confidence")

unlabelled_df["label"] = pd.Series(map(lambda pred: labels[int(pred)], Y_pred))
unlabelled_df["confidence"] = pd.Series(Y_conf, index=unlabelled_df.index)

unlabelled_df = unlabelled_df[["repo", "label", "confidence"]]
unlabelled_df.to_csv("part_two.csv", index=False)

correct = unlabelled_df[np.logical_not(selection)]
check = unlabelled_df[selection]
correct.to_csv("correct.csv", index=False)
check.to_csv("to_check.csv", index=False)