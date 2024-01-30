from processing import *


import sys


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


data = pd.read_csv("sample.csv")  # Replace with your CSV filename

# Define the features (from your list) and label
features = []  # Replace with your actual features
label = data['label_num'].head(2) # Replace with your actual label column name
length = len(data)

count = 0
for i in data['text']:
    count+=1
    text = clean_text(i)
    grammatical_errors = extract_grammatical_errors(text)
    feature = extract_features(text, grammatical_errors)
    features.append(feature)
    progress(count,length)
    

# Select only the specified features and label from the dataset


# Create the Random Forest classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)  # Example parameters

# Train the model on the CSV data
model.fit(features, label)

# Pickle the trained model for future use
with open("random_forest_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model pickled successfully!")