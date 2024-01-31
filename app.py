import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import sys
from commons import processing as p
import json
filename="commons/phishing_data.json"

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def predict_phishing(model, text):

    # Preprocess the text
    text = p.clean_text(text)
    print(text)

    # Extract grammatical errors
    grammatical_errors = p.extract_grammatical_errors(text)

    # Extract features
    features = p.extract_features(text, grammatical_errors)

    # Predict whether the text is phishing using the machine learning model
    is_phishing = model.predict([features])[0]

    return not is_phishing

def train():

    data = pd.read_csv("datasets/train_sample.csv") 

    label = data['label_num'].head(5)

    text = [i for i in data['text'].head(5)]

    features = []

    model = RandomForestClassifier(n_estimators=100, random_state=42)

    tot = len(text)

    for i in range(len(text)):

        temp = p.clean_text(text[i])
        

        grammatical_errors = p.extract_grammatical_errors(temp)

        feature = p.extract_features(temp, grammatical_errors)

        features.append(feature)
  

        progress(i+1,tot)


    model.fit(features, label)

    with open("model/random_forest_model.pkl", "wb") as f:

        pickle.dump(model, f)

    print("\nModel pickled successfully!")


def test():
    model = pickle.load(open('model/random_forest_model.pkl', 'rb'))

    data = pd.read_csv("datasets/train_sample.csv")

    try:
        with open(filename, 'r') as f:
            temp = json.load(f)
    except FileNotFoundError:
        with open(filename, 'w+') as f:
            temp = {}
            temp["phishing_emails"] = []
            temp["phishing_urls"] = []
            json.dump(temp, f, indent=4)

    text = ["click now urgent https://abcd.com money phishing"]

    for i in text:
        email_domain = p.extract_emails(i)
        url_domain = p.extract_urls(i)
        print(url_domain)
        is_phishing = predict_phishing(model, text)

        if is_phishing:
            print("The text is predicted to be a phishing email")
            if len(email_domain)!=0:
                for i in email_domain:
                    p.add_phishing_email(filename, i)
                    print(f"Email domain '{i}' is newly detected and added to phishing list")
            if len(url_domain)!=0:
                for i in url_domain:
                    p.add_phishing_url(filename, i)
                    print(f"URL domain '{i}' is newly detected and added to phishing list")
        else:
            print("The text is predicted not to be a phishing email")

    
    



if __name__ == "__main__":
    test()
