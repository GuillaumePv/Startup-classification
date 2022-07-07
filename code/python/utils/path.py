import socket

computer_name = socket.gethostname()

if "MBP-de-admin" in computer_name or "MacBook-Pro-de-admin" in computer_name or "pulse" in computer_name or "unil" in computer_name:
    # print("Guillaume's computer")
    path_data = "/Volumes/RECHERCHE/FAC/HEC/SGS/cpeukert/digi/D2c/projects/Software_startups/data/"
    path_data_github = path_data + "github_org_accounts.csv" # generate better path
    path_data_html = path_data + 'html/'

else:
    # print("VM")
    path_data = "S:/projects/Software_startups/data/"
    path_data_github = "S:/projects/ai-specialization/data/github_org_accounts.csv"
    path_data_html = path_data + 'html/'
    path_data_html_selenium = path_data + 'html_selenium/'
    path_github_folder = "S:/data/github/"