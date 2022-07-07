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
from tqdm import tqdm

from parameters import *


pd.set_option('display.max_columns', None)

glovebath = 'glove.6B.50d.txt'

class Model:
    def __init__(self, par : Params()):
        self.par = par
        self.df = pd.read_csv('train_data.csv', sep=',', header=0, encoding="ISO-8859-1")
        self.df = self.create_dataset(self.df)
        self.word2vector = {}
        self.generate_word2vector()

    def create_dataset(self, df: pd.DataFrame):
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

        B2B_downsample = resample(B2B,
                          replace=True,
                          n_samples=len(OTHER),
                          random_state=42)

        B2C_downsample = resample(B2C,
                          replace=True,
                          n_samples=len(OTHER),
                          random_state=42)

        df_final = pd.concat([B2B_downsample, B2C_downsample, OTHER])
        return df_final

    def generate_word2vector(self):
        with open(glovebath, 'r', encoding="utf8") as f:
            words = set()
            for line in f:
                line_ = line.strip()
                words_Vec = line_.split()
                words.add(words_Vec[0])
                self.word2vector[words_Vec[0]] = list(map(float, words_Vec[1:]))

    def emmbedding(self, type, method):
        result = []
        wordsOfDoc = []
        print("=== prepare embeddings ===")
        for i in tqdm(range(len(type))):
            # print(type[i])
            tmp = []
            for j in type[i]:
                # print(j)
                word = nltk.word_tokenize(j)
                wordsOfDoc.append(word)
                for p in word:
                    if p in self.word2vector:
                        tmp.append(self.word2vector[p])
                    else:
                        tmp.append([0] * 50)
                r = [sum(i) if method == "SUM" else sum(i) / len(i) for i in zip(*tmp)]
                result.append(r)
        return result

    def prepare_x(self, df: pd.DataFrame):
        print(("=== prepare data ==="))
        withoutpunc = []
        for i in tqdm(range(len(df.loc[:, ['text']]))):
            x = df.iloc[i]['text'].lower()
            withoutpunc.append([x])
            #print(len(withoutpunc))

        return self.emmbedding(withoutpunc, 'SUM')

    def train(self):
        # create training of the model
        x = self.prepare_x(self.df)
        y = []
        for i in range(len(self.df.loc[:, ['classification']])):
            y.append(self.df.iloc[i]['classification'])
        
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
        model = self.create_model()
        model.fit(X_train, y_train)

        yPrediction = model.predict(X_test)
        print(yPrediction)
        print(classification_report(y_test, yPrediction))
        print(confusion_matrix(y_test, yPrediction))

        filename = 'model/RFword2vec_model.sav'
        joblib.dump(model, open(filename, 'wb'))

    def create_model(self):
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


        model_random = RandomizedSearchCV(estimator = model, param_distributions = random_grid, n_iter = 50, cv = 3, verbose=3, random_state=0, n_jobs = -1,error_score='raise')
        return model_random

    def predict(self, df: Params()):
        x = self.prepare_x(df)
        # create method to predict group of the text
        model = joblib.load('model/RFword2vec_model.sav')
        pred_proba = model.predict_proba(x)
        best_proba = []
        for pred in pred_proba:
            best_proba.append(np.max(pred))
        return model.predict(x), best_proba

if __name__ == "__main__":
    par = Params()
    model = Model(par)
    df = pd.read_csv(f"{par.path_dataset}/website_info_cleaned.csv")
    columns_wanted = ["website","text","classification","classification_proba"]
    print(f"shape of the dataset: {df.shape}")
    print("=== run the model ===")
    result = model.predict(df)
    
    df["classification"] = result[0]
    df["classification_proba"] = result[1]
    df.loc[df["classification"] == 0, "classification"] = "B2B"
    df.loc[df["classification"] == 1, "classification"] = "B2C"
    df.loc[df["classification"] == 2, "classification"] = "OTHER"
    print("=== save data ===")
    df[columns_wanted].to_csv(f"{par.path_dataset}/website_classified.csv",index=False)
    