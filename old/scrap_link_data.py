import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import socket

import threading

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
from path import path_data_github, path_data

# Define an output queue
# output = Queue()


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





if __name__ == '__main__':
    print("=== Loading data ===")
    df = pd.read_csv(path_data_github)
    df['urls'] = df['domain'].apply(lambda x: "http://www." + str(x))
    urls = df['urls'].values
    if  os.path.isfile(path_data+"website_done.txt") == False:
        f = open(path_data+'website_done.txt','a')
        f.close()

    print("=== processing urls ===")
    f = open(path_data+'website_done.txt','r')
    number_line = len(f.readlines())+1

    f.close()
    urls = urls[number_line:]
    print("=== Launching algorithms ===")
    for url in tqdm(urls[:]):
        f = open(path_data+'website_done.txt','r')
        if url in f.read():
            f.close()
        else:
            f.close()
            fetch_links(url)
            f = open(path_data+'website_done.txt','a')
            f.write(url+"\n")
            f.close()
    # start=time.time()
    # print("=== Processing ===")
    # with ThreadPoolExecutor(max_workers=25) as p:
    #     p.map(fetch_links,urls[:])

    # # for url in tqdm(urls[:10]):
    # #     fetch_links(url)

    # print("Time Taken: ",str(time.time()-start)) # No optimization: 52sec
# processes=[Process(target=fetch_links,args=(urls,)) for url in tqdm(urls)]

#     # Run processes
# for p in processes:p.start()

    # Get process results from the output queue
# results = [output.get() for p in processes]
# results_df = pd.concat(results)

# results_df.to_csv('D:/multi-process.csv')
    # Exit the completed processes
# for p in processes:p.join()

    
# threads = [threading.Thread(target=fetch_links, args=(url,))
#            for url in tqdm(df['domain'])]

# for t in threads:
#     t.start()



# list_domain = []
# list_html = []
# number_problem = 0
# for domain in tqdm(df["domain"][:]):
#     try:
#         result = requests.get("http://www." + domain)
#         src = result.content
#         soup = BeautifulSoup(src, 'html.parser')
#     except Exception:
#         soup = ""
#         number_problem += 1

#     list_domain.append(domain)
#     list_html.append(soup)

# data = {
#     "domain_link":list_domain,
#     "html_website":list_html
# }
# df_scrapper = pd.DataFrame(data)
# total_domain = len(df[domain])
# print(f"{(number_problem/total_domain)*100}% link problem")
# print(df_scrapper)
