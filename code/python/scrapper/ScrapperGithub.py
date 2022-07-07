import pandas as pd
import requests
from tqdm import tqdm

import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)

sys.path.append(parentdir+"/utils/")
from path import path_github_folder

class ScrapperGithub:
    def __init__(self,path_df,is_csv=True):
        if is_csv:
            self.df = pd.read_csv(path_df)
        else:
            self.df = pd.read_excel(path_df)

        self.save_dir = path_github_folder

    def scrap_readme(self):
        repos = self.df["repo"]
        text_repos = []
        for repo in tqdm(repos):
            url = f"https://raw.githubusercontent.com/{repo}/master/README.md"
            r = requests.get(url)
            try:
                content = str(r.content, encoding="utf-8")
            except UnicodeDecodeError:
                content = str(r.content)
            text_repos.append(content)

        self.df["repo_text"] = text_repos

    def create_dataset(self):
        df_text = pd.read_csv("./download/github_done.txt",names=["file","name_account","name_repo",""]).iloc[:,:-1]
        print(df_text.shape)
        list_repo = []
        for i in tqdm(range(df_text.shape[0])):
            value = str(df_text["name_account"].loc[i])+"/"+str(df_text["name_repo"].loc[i])
            list_repo.append(value)
        
        df_text["repo"] = list_repo
        print("=== load file ===")
        list_file = os.listdir(path_github_folder + "/good_readme/")
        print(f"number of file: {len(list_file)}")
        list_text = []
        for file in tqdm(list_file):
            f = open(path_github_folder + "/good_readme/" + file, encoding="utf-8")
            text = f.read()
            list_text.append(text)

        df_text["text"] = list_text

        df_text.to_csv(path_github_folder + "unclassified_new_github.csv", index=False)
        
if __name__ == "__main__":
    path = path_github_folder + "external_repo_classification.xlsx"
    scrapperGithub = ScrapperGithub(path, False)
    # scrapperGithub.scrap_readme()
    # scrapperGithub.df.to_csv(path_github_folder + "external_repo_classification.csv",index=False)
    scrapperGithub.create_dataset()