import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

path_data_github = "Z:/projects/ai-specialization/data/github_org_accounts.csv"

df = pd.read_csv(path_data_github)

list_domain = []
list_html = []
number_problem = 0
for domain in tqdm(df["domain"][:]):
    try:
        result = requests.get("http://www." + domain)
        src = result.content
        soup = BeautifulSoup(src, 'html.parser')
    except Exception:
        soup = ""
        number_problem += 1

    list_domain.append(domain)
    list_html.append(soup)

data = {
    "domain_link":list_domain,
    "html_website":list_html
}
df_scrapper = pd.DataFrame(data)
total_domain = len(df[domain])
print(f"{(number_problem/total_domain)*100}% link problem")
# print(df_scrapper)
