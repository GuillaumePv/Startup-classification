import shutil
from tqdm import tqdm
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import sys
import time
import shutil

# Libraries in order to paralel code
from joblib import Parallel, delayed
import multiprocessing
#adding directory to path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)

sys.path.append(parentdir+"/utils/")
from path import path_github_folder


class Github:
    def __init__(self, save_dir, read_dir=None):
        self.save_dir = save_dir
        self.read_dir = read_dir
        self.df_links = None
        self.read_links()
        self.num_cores = multiprocessing.cpu_count()
    
    def read_links(self):
        self.df_links = pd.read_csv(self.read_dir + "internal_repo_actitivity_detail.csv")
        self.df_links = self.df_links.dropna()

    def check_file(self):
        print("=== It takes time to launch ===")
        list_file = os.listdir(self.save_dir)
        error = 0
        # check file aleardy done
        def func_check(file,copy_good=True):
            f = open(self.save_dir+file, encoding="utf-8")
            bug = False
            for line in f.readlines():
                if line == "429: Too Many Requests":
                    f_write = open("./download/github_too_many_requests.txt","a")
                    f_write.write(file+","+line+",\n")
                    f_write.close()
                    # error += 1
                    bug = True
                        # print(line)
                elif line == "400: Invalid request":
                    f_write = open("./download/github_invalid_request.txt","a")
                    f_write.write(file+","+line+",\n")
                    f_write.close()
                    # error += 1
                    bug = True
                        # print(line)
                elif line == "404: Not Found":
                    f_write = open("./download/github_not_found.txt","a")
                    f_write.write(file+","+line+",\n")
                    f_write.close()
                    # error += 1
                    bug = True
            if bug == False:
                login = file.split("_")[0]
                repo = file.split("_")[1].replace(".txt","")
                f_write = open("./download/github_done.txt","a")
                f_write.write(file+","+login+","+repo+",\n")
                f_write.close()
                if copy_good:
                    dest_path = f"{path_github_folder}/good_readme/{file}"
                    shutil.copyfile(self.save_dir+file, dest_path)

                
            f.close()

        # Parallel(n_jobs=self.num_cores)(delayed(func_check)(i) for i in tqdm(list_file))
        for file in tqdm(list_file):
            func_check(file)
        
        print("Number of error: ",error)
        print("% error: ", error/len(list_file))

    def check_github_done(self):
        # check for file done
        pass
    def scrap(self):

        df = pd.read_csv("./download/github_done.txt",names=["textfile","login","repo","unamed"])
        del df["unamed"]
        
        self.df_links["repo_cleaned"] = self.df_links['repo'].apply(lambda x: x.split("/")[1] if len(x.split("/")) == 2 else x)
        list_repo = self.df_links["repo_cleaned"].values
        list_login = self.df_links["login"].values

        def read_me(login, repo, filename):
            
            url_base = "https://github.com"
            
            re = requests.get(f"https://github.com/{login}/{repo}")
            soup = BeautifulSoup(re.text)

            links = soup.find_all("a")
            for link in links:
                if "README" in link.text:
                    if "master" in link['href'] or "main" in link['href']:
                        re = requests.get(url_base + link['href'].replace("blob",'raw'))
                        if os.path.exists(path_github_folder+"readme/"+f"{filename}.txt"):
                            os.remove(path_github_folder+"readme/"+f"{filename}.txt")
                        f = open(path_github_folder+"readme/"+f"{filename}.txt","w+",encoding="utf-8")
                        f.write(re.text)
                        f.close()

        for i in tqdm(range(len(list_repo[:]))):
            filename = list_login[i] + "_" + list_repo[i]
            if filename in df["textfile"]:
                pass
            else:
                read_me(list_login[i], list_repo[i], filename)

        
# 861990 good
github = Github(path_github_folder+"readme/",path_github_folder)
github.check_file()

