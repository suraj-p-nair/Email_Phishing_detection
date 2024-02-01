from commons.check_json import *
filename = 'commons/phishing_data.json'


def clean_text(text):

    # Remove punctuation
    punc = set(string.punctuation)
    clean_text = ''.join(ch for ch in text if ch not in punc)

    # Convert to lowercase
    clean_text = clean_text.lower()

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    clean_text = [word for word in clean_text.split() if word not in stop_words]

    # Stemming
    stemmer = nltk.PorterStemmer()
    clean_text = [stemmer.stem(word) for word in clean_text]
    return ' '.join(clean_text)



def extract_emails(text):
     # Define the email pattern
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"

    # Find all email addresses
    matches = re.findall(email_pattern, text)

    # Extract and return only the domain names
    

    return matches

def extract_urls(text):
    url_pattern = r"(https?://[^\s]+)"
    urls = re.findall(url_pattern, text)
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

     # Extract email domains
    email_domains = extract_emails(text)

    # Extract URL domains
    url_domains = extract_urls(text)

    # Presence of specific keywords
    keywords = ['phishing', 'scam', 'urgent', 'act now', 'click here', 'win', 'free']
    keyword_features = [1 if keyword in text else 0 for keyword in keywords]

    # Presence of URL patterns
    url_patterns = ['http://', 'https://', '.com']
    url_features = [1 if pattern in text else 0 for pattern in url_patterns]

    # Presence of special characters
    special_characters = ['@', '#', '$', '%', '^', '&', '*', '(', ')']
    special_char_features = [1 if char in text else 0 for char in special_characters]

    # Features based on part-of-speech (POS) tagging

    tokens = nltk.word_tokenize(text)
    tagged_tokens = nltk.pos_tag(tokens)
    pos_counts = {}

    for tag in ['PRP', 'VB', 'VBD','VBG','NN','NNS','JJ','JJR','JJS','RB','RBR','RBS']:
        pos_counts[tag] = 0
    for word, tag in tagged_tokens:
        if tag in ['PRP', 'VB', 'VBD','VBG','NN','NNS','JJ','JJR','JJS','RB','RBR','RBS']: 
            pos_counts[tag] = pos_counts.get(tag, 0) + 1
    pos_features = list(pos_counts.values())  # Convert counts to a list
    
    

    # Previously detected phishing domains
    previously_detected_emails = []
    previously_detected_urls = []

    # Check if extracted domains are already marked as phishing
    for email_domain in email_domains:
        
        if check_phishing_email(filename, email_domain):
            previously_detected_emails.append(email_domain)
            print(f"Email domain '{email_domain}' is already marked as phishing")

    for url_domain in url_domains:
        
        if check_phishing_url(filename, url_domain):
            previously_detected_urls.append(url_domain)
            print(f"URL domain '{url_domain}' is already marked as phishing")

    # Previously detected feature
    previously_detected_feature = 1 if previously_detected_emails or previously_detected_urls else 0

    

    features = keyword_features + url_features + special_char_features  + [ grammatical_errors , previously_detected_feature] + pos_features
    return features





