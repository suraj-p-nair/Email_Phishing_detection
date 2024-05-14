from commons.headers import *
legitimate_domains = pd.read_csv("dfeatures/legi_domains.csv")
legitimate_domains = legitimate_domains["domain"].to_list()

json_file_path = "commons/phishing_data.json"

async def check_phishing_email(email_domain):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        return 1 if any(domain in data["phishing_emails"] and domain not in legitimate_domains for domain in email_domain) else 0

async def check_phishing_url(url_domain):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        return 1 if any(domain in data["phishing_urls"] and domain not in legitimate_domains for domain in url_domain) else 0

async def add_phishing_email(email_domains):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        if email_domains:
            for domain in email_domains:
                if domain not in data["phishing_emails"]:
                    data["phishing_emails"].append(domain)
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

async def add_phishing_url(url_domains):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        if url_domains:
            for domain in url_domains:
                if domain not in data["phishing_urls"] and domain not in legitimate_domains:
                    data["phishing_urls"].append(domain)
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)


