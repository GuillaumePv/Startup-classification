import socket

computer_name = socket.gethostname()
print(computer_name)

if "MBP-de-admin" in computer_name or "MacBook-Pro-de-admin" in computer_name or "pulse" in computer_name:
    # print("Guillaume's computer")
    path_data = "/Volumes/RECHERCHE/FAC/HEC/SGS/cpeukert/digi/D2c/projects/ai-specialization/data/"
    path_data_github = path_data + "github_org_accounts.csv" # generate better path
    path_data_html = path_data + 'html/'

else:
    # print("VM")
    path_data = "Z:/"
    path_data_github = "Z:/projects/ai-specialization/data/github_org_accounts.csv"
    path_data_html = "Z:/projects/ai-specialization/html"