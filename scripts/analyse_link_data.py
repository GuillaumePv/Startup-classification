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

computer_name = socket.gethostname()
print(computer_name)
if "MBP-de-admin" in computer_name or "MacBook-Pro-de-admin" in computer_name or "pulse" in computer_name:
    # print("Guillaume's computer")
    path_data = "/Volumes/RECHERCHE/FAC/HEC/SGS/cpeukert/digi/D2c/projects/ai-specialization/data/"
    path_data_github = path_data + "github_org_accounts.csv" # generate better path

else:
    # print("VM")
    path_data = "Z:/projects/ai-specialization/data"
    path_data_github = path_data + "/github_org_accounts.csv"

 # Define an output queue
# output = Queue()
print("=== Loading data ===")
df = pd.read_csv(path_data_github)
df['domain'] = df['domain'].apply(lambda x: "http://www." + str(x))

# list_problem_link = []
def fetch_links(url):
    try:
        r = requests.get(url)
        filename = path_data + '/output/' +url.split('/')[-1]+'.html'

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



if __name__ == '__main__':
    start=time.time()
    print("=== Processing ===")
    with ThreadPoolExecutor(max_workers=25) as p:
        p.map(fetch_links,urls[:])

    # for url in tqdm(urls[:10]):
    #     fetch_links(url)

    print("Time Taken: ",str(time.time()-start)) # No optimization: 52sec
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
