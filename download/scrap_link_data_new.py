import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from tqdm import tqdm
import socket

import threading
from joblib import Parallel, delayed
import multiprocessing
## Parallezing
import asyncio

import time

from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor

import os
import sys
#adding directory to path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)

sys.path.append(parentdir+"/utils/")
from path import path_data_github, path_data, path_data_html, path_data_html_selenium

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("enable-automation")
# Define an output queue
# output = Queue()


# list_problem_link = []
def fetch_links(domain,url):
    try:

        if os.path.isdir(path_data_html+domain):
            pass
        else:
            os.makedirs(path_data_html+domain)
            r = requests.get(url)
            filename = path_data_html+ domain + "/" +url.split('/')[-1]+'.html'
            with open(filename,'wb') as f:
                f.write(r.content)
        # soup = BeautifulSoup(r.content,'html.content')
        # print(soup)
    except Exception as e:
        pass
        # list_problem_link.append(url)
        # print(str(e))

    print('.',end="",flush=True)


def fetch_links_selenium(domain, url):
    try:
        if os.path.isdir(path_data_html_selenium+domain):
            pass
        else:
            os.makedirs(path_data_html_selenium+domain)
            driver =webdriver.Chrome('driver/chromedriver_98',options=chrome_options)
            driver.get(url)
            r = driver.page_source
           
            filename = path_data_html_selenium+ domain + "/" +url.split('/')[-1]+'.html'
            with open(filename,'wb') as f:
                f.write(r)
            
            driver.close()
        # soup = BeautifulSoup(r.content,'html.content')
        # print(soup)
    except Exception as e:
        pass
        # list_problem_link.append(url)
        # print(str(e))
    

if __name__ == '__main__':
    num_cores = multiprocessing.cpu_count()
    print(f"== number of CPU: {num_cores} ==")
    print("=== Loading data ===")
    df = pd.read_csv(path_data_github)
    df['urls'] = df['domain'].apply(lambda x: "http://www." + str(x))

    website_done = os.listdir(path_data_html_selenium)
    number_done = len(website_done)
    print(f"=== already done {number_done} ===")
    df_final = df[["domain","urls"]]
    df_final = df_final.iloc[number_done:,:]
    urls = df_final['urls'].values
    domains = df_final['domain'].values

    start=time.time()
    print("=== Processing ===")

    Parallel(n_jobs=num_cores)(delayed(fetch_links_selenium)(domains[i], urls[i]) for i in tqdm(range(len(urls))))
    # array = [(, i) for i in range(len(df_final))]
    # with ThreadPoolExecutor(max_workers=30) as p:
    #     p.map(fetch_links,domains[:],urls[:])

    print("Time Taken: ",str(time.time()-start)) # No optimization: 52sec



