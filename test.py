from processing import *

def predict_phishing(model, text):
    """
    Predicts whether the text is a phishing email or not using a machine learning model.
    Args:
        model: The trained machine learning model.
        text: The text to predict on.
    Returns:
        is_phishing: True if the model predicts it's phishing, False otherwise.
    """

    # Preprocess the text
    text = clean_text(text)

    # Extract grammatical errors
    grammatical_errors = extract_grammatical_errors(text)

    # Extract features
    features = extract_features(text, grammatical_errors)

    # Predict whether the text is phishing using the machine learning model
    is_phishing = model.predict([features])[0]

    return is_phishing


def main():
    # Load the machine learning model
    model = pickle.load(open('phishing_model.pkl', 'rb'))

    # Load the JSON file of known phishing domains
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
    # The file does not exist, so create it
        with open(filename, 'w+') as f:
            data = {}
            json.dump(data, f)

    # Get the text to analyze
    text = input("Enter the text to analyze: ")

    # Extract email domains and URL domains
    email_domains = extract_emails(text)
    url_domains = extract_urls(text)

    # Check if extracted domains are already marked as phishing
    for email_domain in email_domains:
        if check_phishing_email(filename, email_domain):
            print(f"Email domain '{email_domain}' is already marked as phishing")
            

    for url_domain in url_domains:
        if check_phishing_url(filename, url_domain):
            print(f"URL domain '{url_domain}' is already marked as phishing")

    # Predict whether the text is phishing using the machine learning model
    is_phishing = predict_phishing(model, text)

    if is_phishing:
        print("The text is predicted to be a phishing email")
        add_phishing_email(filename, email_domain)
        print(f"Email domain '{email_domain}' is newly detected and added to phishing list")
        add_phishing_url(filename, url_domain)
        print(f"URL domain '{url_domain}' is newly detected and added to phishing list")
    else:
        print("The text is predicted not to be a phishing email")

if __name__ == "__main__":
    main()

