from googleapiclient.discovery import build 
from google_auth_oauthlib.flow import InstalledAppFlow 
from google.auth.transport.requests import Request 
import pickle 
import os.path 
#import base64 
#import email 
#from bs4 import BeautifulSoup 
import regex as re

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'] 

f = open("api_results.txt",'w', encoding="utf-8")
def extract_urls(text):
    url_regex = r"\b(?:https?://)?(?:www\.)?([a-zA-Z0-9]+\.(?:com|org|net|in|[a-z]{2})(?:/[a-zA-Z0-9_\-.~:/?#[\]@!$&'()*+,;=]*|))"
    urls = re.findall(url_regex, text)
    return "\n".join(urls)

def extract_emails(text):

    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"

    matches = re.findall(email_pattern, text)

    return "\n".join(matches)

def getEmails(): 
	creds = None
	if os.path.exists('token.pickle'): 
		with open('token.pickle', 'rb') as token: 
			creds = pickle.load(token)

	if not creds or not creds.valid: 
		if creds and creds.expired and creds.refresh_token: 
			creds.refresh(Request()) 
		else: 
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES) 
			creds = flow.run_local_server(port=0) 

		with open('token.pickle', 'wb') as token: 
			pickle.dump(creds, token) 
		

	service = build('gmail', 'v1', credentials=creds) 

	result = service.users().messages().list(userId='me').execute() 


	messages = result.get('messages') 

	
	for msg in messages: 
		txt = service.users().messages().get(userId='me', id=msg['id']).execute() 

		ans = ""
		ans += "BODY:	" + (txt['snippet'] + "\n")

		txt = txt['payload']['headers']
		
		for i in txt:
			if i['name'] == "To":
				ans += "TO:		"+(str(i['value']) + "\n")
			if i['name'] == "Subject":
				ans += "SUBJECT:	" + (str(i['value']) + "\n")
			if i['name'] == "From":
				ans += "FROM:	" + (str(i['value']) + "\n")
		f.write(str(ans))

		print(extract_urls(ans))
		print(extract_emails(ans))
		break


getEmails()
