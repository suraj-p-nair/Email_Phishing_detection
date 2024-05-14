from commons.processing_sample import *

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'] 

async def getEmails():
    creds = None
    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                with open('token.pkl', 'wb') as token:
                    pickle.dump(creds, token)
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.pkl', 'wb') as token:
                pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    result = service.users().messages().list(userId='me',maxResults=10).execute()
    messages = result.get('messages') 
    full_ans = []
    for msg in messages: 
        features = []
        txt = service.users().messages().get(userId='me', id=msg['id']).execute() 
        email_data = {}
        headers = txt['payload']['headers']
        for i in headers:
            if i['name'] == "From":
                email_data["From"] = str(i['value'])
            if i['name'] == "Subject":
                email_data["Subject"] = str(i['value'])
        
        email_data["Body"] = txt['snippet']
        features = await extract_features(email_data["Subject"] + email_data["Body"])
        features = [float(item) for item in features]
        features_df = pd.DataFrame([features], columns=feature_column_names)
        
        result = phishing_model.predict(features_df)
        if result:
            await add_phishing_url( await extract_url_domain( await extract_urls(email_data["Subject"]+email_data["Body"]) ) )
        email_data["ModelResult"] = result
        full_ans.append(email_data)
    return full_ans

