import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import sys
import processing_sample as p
import json
import os
import asyncio

filename = 'commons/phishing_data.json'
model_file_path = "model/phishing_model.pkl"
f = open("api_results.txt", 'w', encoding="utf-8")

previously_detected_emails = []
previously_detected_urls = []


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


async def check_phishing_email_async(filename, email_domain):
    with open(filename, 'r') as fr:
        try:
            data = json.load(fr)
        except:
            pass
    return email_domain in data["phishing_emails"]


async def check_phishing_url_async(filename, url_domain):
    with open(filename, 'r') as fr:
        try:
            data = json.load(fr)
        except:
            pass
    return url_domain in data["phishing_urls"]


async def predict_phishing_async(model, text):
    text = await p.clean_text(text)
    grammatical_errors = await p.extract_grammatical_errors(text)
    features = await p.extract_features(text, grammatical_errors)
    is_phishing = model.predict([features])
    return is_phishing


async def train():
    data = pd.read_csv("datasets/phishing.csv")
    count = 15000
    label = data['Email Type'].head(count)
    text = [i for i in data['Email Text'].head(count)]
    features = []
    model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=4)

    for i in range(len(text)):
        print(i)
        if pd.isna(text[i]):
            text[i] = ""
        if len(text[i]) > 1000:
            text[i] = text[i][0:1000]

        temp = await p.clean_text(text[i])
        grammatical_errors = await p.extract_grammatical_errors(temp)
        feature = await p.extract_features(temp, grammatical_errors)
        features.append(feature)

        if label[i]:
            email_domains = await p.extract_emails(text[i])
            url_domains = await p.extract_urls(text[i])

            for email_domain in email_domains:
                if await check_phishing_email_async(filename, email_domain):
                    previously_detected_emails.append(email_domain)

            for url_domain in url_domains:
                if await check_phishing_url_async(filename, url_domain):
                    previously_detected_urls.append(url_domain)

            if len(email_domains) != 0:
                for j in email_domains:
                    if j not in previously_detected_emails:
                        await p.add_phishing_email(filename, j)

            if len(url_domains) != 0:
                for k in url_domains:
                    if k not in previously_detected_urls:
                        await p.add_phishing_url(filename, k)

        progress(i + 1, count)

    model.fit(features, label)

    with open("model/phishing_model_sample.pkl", "wb") as f:
        pickle.dump(model, f)

    print("\nModel pickled successfully!")


async def test():
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

        is_phishing = await predict_phishing_async(model, text[i])

        if is_phishing[0]:
            if (is_phishing[0] == data['Email Type'][i]):
                acc += 1
            email_domains = await p.extract_emails(text[i])
            url_domains = await p.extract_urls(text[i])

            for email_domain in email_domains:
                if await check_phishing_email_async(filename, email_domain):
                    previously_detected_emails.append(email_domain)

            for url_domain in url_domains:
                if await check_phishing_url_async(filename, url_domain):
                    previously_detected_urls.append(url_domain)

            if len(email_domains) != 0:
                for j in email_domains:
                    if j not in previously_detected_emails:
                        await p.add_phishing_email(filename, j)

            if len(url_domains) != 0:
                for k in url_domains:
                    if k not in previously_detected_urls:
                        await p.add_phishing_url(filename, k)

        progress(i + 1, count)

    print(acc, '/', count, '=', (acc / count) * 100, '%')


if __name__ == "__main__":
    asyncio.run(train())
    asyncio.run(test())
