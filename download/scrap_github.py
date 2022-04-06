from cgitb import text
import pandas as pd
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from joblib import Parallel, delayed
import multiprocessing
import time
import time

import os
import sys
#adding directory to path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)

sys.path.append(parentdir+"/utils/")
from path import path_github_folder

"""
400: Invalid request
"""
df = pd.read_csv("./download/github_done.txt",names=["textfile","login","repo","unamed"])
del df["unamed"]
def scrap_readme(repository, login):
    number_read_me = 0
    
    path = path_github_folder+"readme/"+repository+"/"
    # if os.path.isdir(path):
    #     pass
    # else:
    #     os.makedirs(path)

    filename = login+"_"+repository

    
    if filename in df["textfile"].values:
        pass
    else:
        if os.path.exists(path_github_folder+"readme/"+f"{filename}.txt"):
            os.remove(path_github_folder+"readme/"+f"{filename}.txt")

        repo_url = login+"/"+repository
        f = open("./download/repo_done.txt","a")
        f.write(repo_url+",\n")
        f.close()
        url = f"https://raw.githubusercontent.com/{repo_url}/master/README.md"
        r = requests.get(url)

        try:
            content = str(r.content, encoding="utf-8")
            if content == "429: Too Many Requests":
                print("=== scraper blocked ====")
                time.sleep(60)
                    # os._exit(0)
        except Exception:
            content = str(r.content)
            if content == "429: Too Many Requests":
                print("=== scraper blocked ====")
                time.sleep(60)
                    # os._exit(0)
        if 'Not Found' in content:
            url = f"https://raw.githubusercontent.com/{repo_url}/main/README.md"
            r = requests.get(url)
            try:
                content = str(r.content, encoding="utf-8")
                if content == "429: Too Many Requests":
                    print("=== scraper blocked ====")
                    time.sleep(60)
                    # os._exit(0)
                f = open(path_github_folder+"readme/"+f"{filename}.txt","w+",encoding="utf-8")
                f.write(content)
                f.close()
            except Exception:
                content = str(r.content)
                if content == "429: Too Many Requests":
                    print("=== scraper blocked ====")
                    time.sleep(60)
                    # os._exit(0)
                try:
                    f = open(path_github_folder+"readme/"+f"{filename}.txt","w+",encoding="utf-8")
                    f.write(content)
                    f.close()
                    number_read_me += 1
                except FileNotFoundError:
                    print("file not found")
                    pass
        else:
            f = open(path_github_folder+"readme/"+f"{filename}.txt","w+",encoding="utf-8")
            f.write(content)
            f.close()
            number_read_me += 1
    
    # print('.',end="",flush=True)

if __name__ == '__main__':
    # number_done = int(input("how much github links done ?"))
    num_cores = multiprocessing.cpu_count()
    print(f"== number of CPU: {num_cores} ==")
    print("=== Loading data ===")
    
    # github_done = os.listdir(path_github_folder+"readme/")
    # number_done = len(github_done)
    # print(f"number done: {number_done}")
    df_test = pd.read_csv(path_github_folder+"internal_repo_actitivity_detail.csv")
    # print(df_test.head(5))

    df_test = df_test.dropna()
    print(df_test.shape)
    df_test = df_test.iloc[899393+912168:,:]
    # 899393
    start=time.time()
    print("=== Processing ===")

    df_test["repo_cleaned"] = df_test['repo'].apply(lambda x: x.split("/")[1] if len(x.split("/")) == 2 else x)
    list_repo = df_test["repo_cleaned"].values
    list_login = df_test["login"].values
    # for repo in  df_test["repo"].values:
    #     try:
    #         if len(repo.split("/")) == 2:
    #             print(repo.split("/")[1])
    #     except Exception:
    #         print(repo)
    #         break
    # array = [(, i) for i in range(len(df_final))]
    for i in tqdm(range(len(list_repo[:]))):
        scrap_readme(list_repo[i], list_login[i])
    # Parallel(n_jobs=num_cores)(delayed(scrap_readme)(list_repo[i], list_login[i]) for i in tqdm(range(len(list_repo))))
    # with ThreadPoolExecutor(max_workers=30) as p:
    #     p.map(scrap_readme,list_repo[number_done:],list_login[number_done:])

    print("Time Taken: ",str(time.time()-start)) # No optimization: 52sec

