import pandas as pd, re, string, nltk, pickle, json, sys, os, asyncio, math, joblib, pickle
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.ensemble import RandomForestClassifier
import Levenshtein
from fuzzywuzzy import fuzz
from textblob import TextBlob
from commons.check_json import check_phishing_email, check_phishing_url, add_phishing_email, add_phishing_url
from googleapiclient.discovery import build 
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow 
from google.auth.transport.requests import Request 

legitimate_domains = pd.read_csv("datasets/legi_domains.csv")
legitimate_domains = legitimate_domains["domain"].to_list()


column_names_url = [
    "url_length", "number_of_dots_in_url", "having_repeated_digits_in_url", "number_of_digits_in_url",
    "number_of_special_char_in_url", "number_of_hyphens_in_url", "number_of_underline_in_url",
    "number_of_slash_in_url", "number_of_questionmark_in_url", "number_of_equal_in_url",
    "number_of_at_in_url", "number_of_dollar_in_url", "number_of_exclamation_in_url",
    "number_of_hashtag_in_url", "number_of_percent_in_url", "domain_length", "number_of_dots_in_domain",
    "number_of_hyphens_in_domain", "having_special_characters_in_domain", "number_of_special_characters_in_domain",
    "having_digits_in_domain", "number_of_digits_in_domain", "having_repeated_digits_in_domain",
    "number_of_subdomains", "having_dot_in_subdomain", "having_hyphen_in_subdomain",
    "average_subdomain_length", "average_number_of_dots_in_subdomain", "average_number_of_hyphens_in_subdomain",
    "having_special_characters_in_subdomain", "number_of_special_characters_in_subdomain",
    "having_digits_in_subdomain", "number_of_digits_in_subdomain", "having_repeated_digits_in_subdomain",
    "having_path", "path_length", "having_query", "having_fragment", "having_anchor",
    "entropy_of_url", "entropy_of_domain"
]



phishing_model = joblib.load(open("models/final_modified_model_latest.pkl", "rb"))
url_model = pickle.load(open("models/url_model", "rb"))
dataset = pd.read_csv("datasets/phishing.csv")
#features = pd.read_csv("features/phishing_features.csv")
keywords = pd.read_csv("features/keywords.csv")


sia = SentimentIntensityAnalyzer()

feature_column_names = ["num_of_url_feature", "len_of_urls_feature", "misspell1", "misspell2", "url_feature",
                        "previously_detected_feature", "spelling_mistake_feature", "pos_tag_feature1",
                        "pos_tag_feature2", "pos_tag_feature3", "pos_tag_feature4", "pos_tag_feature5",
                        "pos_tag_feature6", "pos_tag_feature7", "pos_tag_feature8", "pos_tag_feature9",
                        "pos_tag_feature10", "pos_tag_feature11", "pos_tag_feature12", "sentiment_feature1",
                        "sentiment_feature2", "sentiment_feature3", "sentiment_feature4","path_length", "having_query",
                        "having_fragment", "having_anchor_tag", "entropy_of_url", "entropy_of_domain","legit_domains"]





