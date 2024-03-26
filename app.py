import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import sys
from commons import processing as p
import json
filename="commons/phishing_data.json"

count = 10

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def predict_phishing(model, text):

    text = p.clean_text(text)

    grammatical_errors = p.extract_grammatical_errors(text)

    features = p.extract_features(text, grammatical_errors)


    is_phishing = model.predict([features])
   

    return is_phishing

def train():

    data = pd.read_csv("datasets/train_sample.csv") 

    label = data['label_num'].head(count)

    text = [i for i in data['text'].head(count)]

    features = []

    model = RandomForestClassifier(n_estimators=50, random_state=42)


    for i in range(len(text)):

        temp = p.clean_text(text[i])
        

        grammatical_errors = p.extract_grammatical_errors(temp)

        feature = p.extract_features(temp, grammatical_errors)

        features.append(feature)
  

        progress(i+1,count)


    model.fit(features, label)

    with open("model/phishing_model.pkl", "wb") as f:

        pickle.dump(model, f)

    print("\nModel pickled successfully!")


def test():
    model = pickle.load(open('model/phishing_model.pkl', 'rb'))

    data = pd.read_csv("datasets/train_sample.csv")

    text = [i for i in data['text'].head(count)]

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
        email_domain = p.extract_emails(text[i])
        url_domain = p.extract_urls(text[i])
        is_phishing = predict_phishing(model, text[i])

        if is_phishing[0]:
            if(is_phishing[0] == data['label_num'][i]):
                acc+=1
            print("The text is predicted to be a phishing email")
            if len(email_domain)!=0:
                for j in email_domain:
                    p.add_phishing_email(filename, j)
                    print(f"Email domain '{j}' is newly detected and added to phishing list")
            if len(url_domain)!=0:
                for k in url_domain:
                    p.add_phishing_url(filename, k)
                    print(f"URL domain '{k}' is newly detected and added to phishing list")
        else:
            print("The text is predicted not to be a phishing email")
        progress(i+1,count)

    print(acc,'/',count,'=',(acc/count)*100,'%')
    
if __name__ == "__main__":
    test()