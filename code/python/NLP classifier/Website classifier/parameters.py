import numpy as np

import os
import sys
#adding directory to path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir+"/utils/")
from path import path_data

class ParamsRF:
    def __init__(self):
        self.n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]

        self.max_features = ['auto', 'sqrt']
        self.max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
        self.max_depth.append(None)
        self.min_samples_split = [2, 5, 10]
        self.min_samples_leaf = [1, 2, 4]
        self.bootstrap = [True, False]
        self.random_grid = {'n_estimators': self.n_estimators,
                    'max_features': self.max_features,
                    'max_depth': self.max_depth,
                    'min_samples_split': self.min_samples_split,
                    'min_samples_leaf': self.min_samples_leaf,
                    'bootstrap': self.bootstrap}

    

class Params:
    def __init__(self):
        self.paramsRF = ParamsRF()
        self.test_size = 0.2
        self.path_read = ""
        self.path_save = ""
        self.path_dataset = path_data
