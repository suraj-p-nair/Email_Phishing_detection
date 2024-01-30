from headers import *
data = ""
def check_phishing_email(filename, email_domain):
    """
    Checks if an email domain is marked as phishing in the JSON file.
    Args:
        filename: The path to the JSON file.
        email_domain: The email domain to check.
    Returns:
        is_phishing: True if the email domain is marked as phishing, False otherwise.
    """
    with open(filename, 'r') as f:
        try:
            data = json.load(f)
        except:
            pass
    return email_domain in data["phishing_emails"]


def check_phishing_url(filename, url_domain):
    """
    Checks if a URL domain is marked as phishing in the JSON file.
    Args:
        filename: The path to the JSON file.
        url_domain: The URL domain to check.
    Returns:
        is_phishing: True if the URL domain is marked as phishing, False otherwise.
    """
    with open(filename, 'r') as f:
        try:
            data = json.load(f)
        except:
            pass
    return url_domain in data["phishing_urls"]


def add_phishing_email(filename, email_domain):
    """
    Adds a phishing email domain to the JSON file.
    Args:
        filename: The path to the JSON file.
        email_domain: The email domain to add.
    """
    with open(filename, 'r') as f:
        data = json.load(f)
        data["phishing_emails"].append(email_domain)

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def add_phishing_url(filename, url_domain):
    """
    Adds a phishing URL domain to the JSON file.
    Args:
        filename: The path to the JSON file.
        url_domain: The URL domain to add.
    """
    with open(filename, 'r') as f:
        data = json.load(f)
        data["phishing_urls"].append(url_domain)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)