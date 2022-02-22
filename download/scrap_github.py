import pandas as pd
import requests

from path import path_github_folder

df_test = pd.read_csv(path_github_folder+"internal_repo_actitivity_detail.csv")
print(df_test.head(5))