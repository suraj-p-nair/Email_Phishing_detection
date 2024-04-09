import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import sys
from commons import processing as p
import json
import os
filename="commons/phishing_data.json"
model_file_path = "model/phishing_model.pkl"
f = open("api_results.txt",'w', encoding="utf-8")

previously_detected_emails = []
previously_detected_urls = []


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

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


def predict_phishing(model, text):

    text = p.clean_text(text)

    grammatical_errors = p.extract_grammatical_errors(text)

    features = p.extract_features(text, grammatical_errors)


    is_phishing = model.predict([features])
   

    return is_phishing

def train():

    data = pd.read_csv("datasets/phishing.csv") 

    count = 15000

    label = data['Email Type'].head(count)

    text = [i for i in data['Email Text'].head(count)]

    features = []
    if os.path.exists(model_file_path):
    # Load the existing model
        with open(model_file_path, "rb") as f:
            model = pickle.load(f)
        print("Existing model loaded.")
    else:
        model = RandomForestClassifier(n_estimators=50, random_state=42,n_jobs=4)

    

    for i in range(len(text)):
        print(i)
        if pd.isna(text[i]):
            text[i] = ""
        if len(text[i]) > 1000:
            text[i] = text[i][0:1000]
        #print(data['index'][i])

        temp = p.clean_text(text[i])
        
        grammatical_errors = p.extract_grammatical_errors(temp)

        feature = p.extract_features(temp, grammatical_errors)

        features.append(feature)
              
        #print(label[i])

        if label[i]:
            email_domains = p.extract_emails(text[i])

            url_domains = p.extract_urls(text[i])

            for email_domain in email_domains:
        
                if check_phishing_email(filename, email_domain):
                    previously_detected_emails.append(email_domain)
                    #print(f"Email domain '{email_domain}' is already marked as phishing")

            for url_domain in url_domains:
        
                if check_phishing_url(filename, url_domain):
                    previously_detected_urls.append(url_domain)
                    #print(f"URL domain '{url_domain}' is already marked as phishing")


            if len(email_domains)!=0:
                for j in email_domains:
                    if j not in previously_detected_emails:
                        p.add_phishing_email(filename, j)
                        #print(f"Email domain '{j}' is newly detected and added to phishing list")
            if len(url_domains)!=0:
                for k in url_domains:
                    if k not in previously_detected_urls:
                        p.add_phishing_url(filename, k)
                        #print(f"URL domain '{k}' is newly detected and added to phishing list")
        progress(i+1,count)


    model.fit(features, label)

    with open("model/phishing_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("\nModel pickled successfully!")


def test():
    count = 5000
    model = pickle.load(open('model/phishing_model.pkl', 'rb'))

    data = pd.read_csv("datasets/phishing.csv")

    text = [i for i in data['Email Text'].head(count)]

    try:
        with open(filename, 'r') as f:
            temp = json.load(f)
    except FileNotFoundError:
        with open(filename, 'w+') as f:
            temp = {}
            temp["phishing_emails"] = []
            temp["phishing_urls"] = []
            json.dump(temp, f, indent=4)

    acc = 0
    
    for i in range(len(text)):
        if pd.isna(text[i]):
            text[i] = ""
        if len(text[i]) > 1000:
            text[i] = text[i][0:1000]
        is_phishing = predict_phishing(model, text[i])

        if is_phishing[0]:
            if(is_phishing[0] == data['Email Type'][i]):
                acc+=1
            email_domains = p.extract_emails(text[i])

            url_domains = p.extract_urls(text[i])

            for email_domain in email_domains:
        
                if check_phishing_email(filename, email_domain):
                    previously_detected_emails.append(email_domain)
                    #print(f"Email domain '{email_domain}' is already marked as phishing")

            for url_domain in url_domains:
        
                if check_phishing_url(filename, url_domain):
                    previously_detected_urls.append(url_domain)
                    #print(f"URL domain '{url_domain}' is already marked as phishing")


            if len(email_domains)!=0:
                for j in email_domains:
                    if j not in previously_detected_emails:
                        p.add_phishing_email(filename, j)
                        #print(f"Email domain '{j}' is newly detected and added to phishing list")
            if len(url_domains)!=0:
                for k in url_domains:
                    if k not in previously_detected_urls:
                        p.add_phishing_url(filename, k)
                        #print(f"URL domain '{k}' is newly detected and added to phishing list")

        progress(i+1,count)

    print(acc,'/',count,'=',(acc/count)*100,'%')
if __name__ == "__main__":
    train()
    test()