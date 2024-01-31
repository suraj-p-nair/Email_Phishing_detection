from commons.headers import *

def check_phishing_email(filename, email_domain):
    with open(filename, 'r') as fr:
        try:
            data = json.load(fr)
        except:
            pass
    return email_domain in data["phishing_emails"]


def check_phishing_url(filename, url_domain):
    with open(filename, 'r') as fr:
        try:
            data = json.load(fr)
        except:
            pass
    return url_domain in data["phishing_urls"]


def add_phishing_email(filename, email_domain):
    with open(filename, 'r') as f:
        data = json.load(f)
        data["phishing_emails"].append(email_domain)
        
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def add_phishing_url(filename, url_domain):
    with open(filename, 'r') as f:
        data = json.load(f)
        data["phishing_urls"].append(url_domain)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)