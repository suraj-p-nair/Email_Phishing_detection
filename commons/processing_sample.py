from commons.check_json import *

async def extract_urls(text):
    if pd.isna(text):
        return []
    url_regex = r"\b(?:https?://)?(?:www\.)?([a-zA-Z0-9]+\.(?:com|org|net|gov|edu|co|io|info|biz|me)(?:/[a-zA-Z0-9_\-.~:/?#[\]@!$&'()*+,;=]*)?)"
    urls = re.findall(url_regex, text)
    return urls

async def extract_url_domain(urls):
    domains = []
    domain_regex = r"(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+)(?:\/|\?|$)"
    for url in urls:
        # Extract domain from URL using regex
        match = re.search(domain_regex, url)
        if match:
            domain = match.group(1)
            domains.append(domain)
    # Remove duplicates
    unique_domains = list(set(domains))
    return unique_domains

async def calculate_entropy(text):
    # Count the frequency of each character
    frequencies = {}
    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1
    
    # Calculate the probability of each character
    total_chars = len(text)
    probabilities = {char: freq / total_chars for char, freq in frequencies.items()}
    
    # Calculate entropy
    entropy = -sum(prob * math.log2(prob) for prob in probabilities.values())
    return entropy

async def extract_url_features(urls, domains):
    features_list = []


    for url, domain in zip(urls, domains):
        feature_values = []
        if url:
            feature_values.append(len(url))
            feature_values.append(url.count('.'))
            feature_values.append(int(any(char.isdigit() and url.count(char * 2) > 0 for char in url)))
            feature_values.append(sum(char.isdigit() for char in url))
            feature_values.append(sum(not char.isalnum() for char in url))
            feature_values.append(url.count('-'))
            feature_values.append(url.count('_'))
            feature_values.append(url.count('/'))
            feature_values.append(url.count('?'))
            feature_values.append(url.count('='))
            feature_values.append(url.count('@'))
            feature_values.append(url.count('$'))
            feature_values.append(url.count('!'))
            feature_values.append(url.count('#'))
            feature_values.append(url.count('%'))

        if domain:
            feature_values.append(len(domain))
            feature_values.append(domain.count('.'))
            feature_values.append(domain.count('-'))
            feature_values.append(int(any(not char.isalnum() for char in domain)))
            feature_values.append(sum(not char.isalnum() for char in domain))
            feature_values.append(int(any(char.isdigit() for char in domain)))
            feature_values.append(sum(char.isdigit() for char in domain))
            feature_values.append(int(any(char.isdigit() and domain.count(char * 2) > 0 for char in domain)))
            subdomains = domain.split('.')[:-1]
            if subdomains:
                feature_values.append(len(subdomains))
                feature_values.append(int(any('.' in subdomain for subdomain in subdomains)))
                feature_values.append(int(any('-' in subdomain for subdomain in subdomains)))
                feature_values.append(int(sum(len(subdomain) for subdomain in subdomains) / len(subdomains)))
                feature_values.append(int(sum(subdomain.count('.') for subdomain in subdomains) / len(subdomains)))
                feature_values.append(int(sum(subdomain.count('-') for subdomain in subdomains) / len(subdomains)))
                feature_values.append(int(any(not char.isalnum() for subdomain in subdomains for char in subdomain)))
                feature_values.append(int(sum(not char.isalnum() for subdomain in subdomains for char in subdomain)))
                feature_values.append(int(any(char.isdigit() for subdomain in subdomains for char in subdomain)))
                feature_values.append(int(sum(char.isdigit() for subdomain in subdomains for char in subdomain)))
                feature_values.append(int(any(char.isdigit() and subdomain.count(char * 2) > 0 for subdomain in subdomains for char in subdomain)))
            else:
                feature_values.extend([0]*11)
            
        
        path = re.findall(r'http[s]?://[^/]+([^?]+)', url)

        if path:
            path = path[0]
            feature_values.append(1)
            feature_values.append(len(path))
        else:
            feature_values.append(0)
            feature_values.append(0)

        feature_values.append(int('?' in url))
        feature_values.append(int('#' in url))

        feature_values.append(int(re.search(r'<a\s+.*?>', url) is not None))

        feature_values.append(await calculate_entropy(url))
        feature_values.append(await calculate_entropy(domain))
        features_list.append(feature_values)

    avg_features = [sum(col) / len(col) if isinstance(col[0], int) else round(sum(col) / len(col), 9) for col in zip(*features_list)]


    avg_features[-2:] = [float('%.9f' % val) for val in avg_features[-2:]]

    return list(map(int, avg_features[:-2])) + avg_features[-2:]

async def extract_pos_features(text):
    tokens = nltk.word_tokenize(text)
    tagged_tokens = nltk.pos_tag(tokens)
    pos_counts = {}

    for tag in ['PRP', 'VB', 'VBD', 'VBG', 'NN', 'NNS', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS']:
        pos_counts[tag] = 0
    
    for word, tag in tagged_tokens:
        if tag in ['PRP', 'VB', 'VBD', 'VBG', 'NN', 'NNS', 'JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS']:
            pos_counts[tag] = pos_counts.get(tag, 0) + 1

    pos_features = list(pos_counts.values())

    return pos_features

async def extract_sentiment_scores(text):
    sentiment_scores = sia.polarity_scores(text)
    sentiment = list(sentiment_scores.values())
    return sentiment

async def detect_misspelled_domain_levenshtein(domains, threshold=2):
    if not domains:
        return 0
    
    for domain in domains:
        for legit_domain in legitimate_domains:
            distance = Levenshtein.distance(domain, legit_domain)
            if distance <= threshold and distance > 0:
                return 1

    return 0

async def detect_misspelled_domain_soundex(domains):
    for domain in domains:
        for legit_domain in legitimate_domains:
            ratio = fuzz.ratio(domain, legit_domain)
            if ratio >= 85 and ratio < 100: 
                return 1
    return 0

async def detect_misspelled_domains(domains_list):
    misspelled_levenshtein = await detect_misspelled_domain_levenshtein(domains_list)
    misspelled_soundex = await detect_misspelled_domain_soundex(domains_list)
    
    return [misspelled_levenshtein, misspelled_soundex]

async def clean_text(text):
    punc = set(string.punctuation)
    url_regex = r"\b(?:https?://)?(?:www\.)?((?!\bthis\W)[a-zA-Z0-9]+\.(?:com|org|net|in|[a-z]{2})(?:/[a-zA-Z0-9_\-.~:/?#[\]@!$&'()*+,;=]*|))"
    urls = re.findall(url_regex, text)
    text_parts = re.split(url_regex, text)
    clean_text = ""
    for i in text_parts:
        if i not in urls:
            clean_text += i
    for i in punc:
        clean_text = clean_text.replace(i, ' ')
    clean_text = ' '.join(clean_text.split())

    clean_text = clean_text.lower()

    stop_words = set(stopwords.words('english'))
    clean_text = [word for word in clean_text.split() if word not in stop_words]

    stemmer = nltk.PorterStemmer()
    clean_text = [stemmer.stem(word) for word in clean_text]
    return ' '.join(clean_text)

async def extract_emails(text):
    if pd.isna(text):
        return []
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"
    matches = re.findall(email_pattern, text)
    return matches

async def extract_grammatical_errors(text):
    original_text = text
    corrected_text = TextBlob(text)
    corrected_text = corrected_text.correct()

    errors = 0

    original_text = original_text.split(' ')
    corrected_text = corrected_text.split(' ')

    for (a, b) in zip(original_text, corrected_text):
        if a != b:
            errors += 1

    return errors

def predict_url_phishing(url):
    phishing_probability = url_model.predict_proba([url])[0][1]
    return phishing_probability

def calculate_average_phishing_probability(email_urls):
    num_urls = len(email_urls)
    total_phishing_probability = sum(predict_url_phishing(url) for url in email_urls)
    average_phishing_probability = total_phishing_probability / num_urls if num_urls > 0 else 0
    return round(average_phishing_probability, 2)  # Round to 2 decimal places

async def extract_features(text):

    emails = await extract_emails(text)
    urls = await extract_urls(text)
    domains = await extract_url_domain(urls)

    legit_domains_feature = [1 if any(domain in legitimate_domains for domain in domains) else 0]

    num_of_url_feature = [len(urls)]

    len_of_urls_feature = [sum(len(i) for i in urls)]

    previously_detected_feature = [1 if await check_phishing_url(domains) or await check_phishing_email(emails) else 0]

    misspell = await detect_misspelled_domains(urls)

    if not urls:
        url_features_list = [0] * 41
    else:
        url_features_list = await extract_url_features(urls,domains)
    url_features = pd.DataFrame([url_features_list], columns=column_names_url)   


    url_feature = url_model.predict(url_features)


    sentiment_feature = await extract_sentiment_scores(text)

    sentiment_feature[1]-=0.1

    text = await clean_text(text)

    spelling_mistake_feature = await extract_grammatical_errors(text)
        
    pos_tag_feature = await extract_pos_features(text)


    return_features = num_of_url_feature + len_of_urls_feature + misspell + [url_feature[0]] + previously_detected_feature + [spelling_mistake_feature] + pos_tag_feature + sentiment_feature + url_features_list[-6:] + legit_domains_feature



    return return_features

