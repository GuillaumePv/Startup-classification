import pandas as pd
import requests

import pdb
import os, re

from os import listdir
import numpy as np

import time

from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor

import os
import sys
#adding directory to path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)

sys.path.append(parentdir+"/utils/")
from path import path_data_github, path_data, path_data_html

class data_reader:

    def __init__(self):
        self.train_dataset = pd.read_excel(path_data+"Β2Β_B2C.xlsx")
        self.possible_website = pd.read_csv(path_data+"github_org_accounts.csv")
        self.scrapped_website = [f for f in listdir(path_data_html)][:]
    ########################
    ## Download html page ##
    ########################

    # need otpimization
    def download_data():
        df = pd.read_csv(path_data_github)
        df['domain'] = df['domain'].apply(lambda x: "http://www." + str(x))

        # list_problem_link = []
        def fetch_links(url):
            try:
                r = requests.get(url)
                filename = path_data + '/html/' +url.split('/')[-1]+'.html'

                with open(filename,'wb') as f:
                    f.write(r.content)
                # soup = BeautifulSoup(r.content,'html.content')
                # print(soup)
            except Exception as e:
                pass
                # list_problem_link.append(url)
                # print(str(e))

            print('.',end="",flush=True)

        urls = df['domain'].values

        start=time.time()
        print("=== Processing ===")
        with ThreadPoolExecutor(max_workers=25) as p:
            p.map(fetch_links,urls[:])

        # for url in tqdm(urls[:10]):
        #     fetch_links(url)
        print("Time Taken: ",str(time.time()-start))

        ##############################
        ## Create dataset with text ##
        ##############################

    def read_html_files():
        files = [f for f in listdir(path_data_html)][:]
        return files
    
    def read_text_dataset():
        df = pd.read_csv(f'{path_data}/website_info.csv')
        return df
           

if __name__ == "__main__":
    data = data_reader()
    print(data.train_dataset)
    print(len(data.scrapped_website))
    print("===========")
   