from commons.check_json import *
filename = 'commons/phishing_data.json'

def clean_text(text):
    punc = set(string.punctuation)
    url_regex = r"\b(?:https?://)?(?:www\.)?((?!\bthis\W)[a-zA-Z0-9]+\.(?:com|org|net|in|[a-z]{2})(?:/[a-zA-Z0-9_\-.~:/?#[\]@!$&'()*+,;=]*|))"
    urls = re.findall(url_regex, text)
    text_parts = re.split(url_regex, text)
    clean_text = ""
    for i in text_parts:
        if i not in urls:
            clean_text+=i
    for i in punc:
        clean_text=clean_text.replace(i,' ')
    clean_text = ' '.join(clean_text.split())    

    clean_text = clean_text.lower()

    stop_words = set(stopwords.words('english'))
    clean_text = [word for word in clean_text.split() if word not in stop_words]

    stemmer = nltk.PorterStemmer()
    clean_text = [stemmer.stem(word) for word in clean_text]
    return ' '.join(clean_text)



def extract_emails(text):

    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"
    matches = re.findall(email_pattern, text)
    return matches

def extract_urls(text):
    url_regex = r"\b(?:https?://)?(?:www\.)?((?!\bthis\W)[a-zA-Z0-9]+\.(?:com|org|net|in|[a-z]{2})(?:/[a-zA-Z0-9_\-.~:/?#[\]@!$&'()*+,;=]*|))"
    urls = re.findall(url_regex, text)
    return urls

def extract_grammatical_errors(text):
    original_text = text
    corrected_text = TextBlob(text)
    corrected_text = corrected_text.correct()

    errors = 0

    original_text = original_text.split(' ')
    corrected_text = corrected_text.split(' ')

    for (a,b) in zip(original_text,corrected_text):
        if a!=b:
            errors+=1
    
    return errors


def extract_features(text, grammatical_errors):
    email_domains = extract_emails(text)

    url_domains = extract_urls(text)

    keywords = ["Urgent action required", "Immediate attention required", "Account suspended", "Account compromised", "Security alert", "Emergency", "PayPal", "Bank of America", "Amazon", "Apple", "Microsoft", "IRS", "Social Security Administration", "Netflix", "Invoice", "Payment confirmation", "Tax refund", "Wire transfer", "Payment overdue", "Unusual activity in your account", "Password reset", "Account verification", "Unusual login attempts", "Account locked", "Update your information", "Verify your identity", "Social Security number", "Credit card number", "Bank account information", "Login credentials", "PIN", "Date of birth", "Mother's maiden name", "Free gift", "Prize winner", "Exclusive offer", "Limited time offer", "Discount code", "Special deal", "Click here", "Login now", "Verify your account", "Confirm your information", "Reset your password", "Update your account", "Dear customer", "Dear valued customer", "Dear user", "Hello", "Hi", "Attached file", "Download file", "Click to view document", "View file"]


    keyword_features = [1 if keyword in text else 0 for keyword in keywords]

    url_patterns = ['http://', 'https://', '.com']
    url_features = [1 if pattern in text else 0 for pattern in url_patterns]

    special_characters = ['@', '#', '$', '%', '^', '&', '*', '(', ')']
    special_char_features = [1 if char in text else 0 for char in special_characters]

    tokens = nltk.word_tokenize(text)
    tagged_tokens = nltk.pos_tag(tokens)
    pos_counts = {}

    for tag in ['PRP', 'VB', 'VBD','VBG','NN','NNS','JJ','JJR','JJS','RB','RBR','RBS']:
        pos_counts[tag] = 0
    for word, tag in tagged_tokens:
        if tag in ['PRP', 'VB', 'VBD','VBG','NN','NNS','JJ','JJR','JJS','RB','RBR','RBS']: 
            pos_counts[tag] = pos_counts.get(tag, 0) + 1
    

    pos_features = list(pos_counts.values())


    for i in range(len(pos_features)):
        pos_features[i] = round(pos_features[i] / len(text.split(' ')), 3)

    previously_detected_emails = []
    previously_detected_urls = []

    for email_domain in email_domains:
        
        if check_phishing_email(filename, email_domain):
            previously_detected_emails.append(email_domain)
            print(f"Email domain '{email_domain}' is already marked as phishing")

    for url_domain in url_domains:
        
        if check_phishing_url(filename, url_domain):
            previously_detected_urls.append(url_domain)
            print(f"URL domain '{url_domain}' is already marked as phishing")

    previously_detected_feature = 1 if previously_detected_emails or previously_detected_urls else 0

    

    features = keyword_features + url_features + special_char_features  + [ grammatical_errors , previously_detected_feature] + pos_features
    return features





