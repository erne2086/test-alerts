import os.path
import base64
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
receiver = "gdo_data_science@rackspace.com"
SERVICE_ACCOUNT_FILE = '/Users/ejcv/Documents/coding/secrets/rax-datascience-alert-notifier.json'
SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.metadata",
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]
EMAIL_FROM = 'noreply@lyfpedia.com'
EMAIL_TO = 'ejcv.123@gmail.com'
EMAIL_SUBJECT = 'Hello World'
EMAIL_CONTENT = 'Hello World'

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    credentials = service_account.Credentials.from_service_account_file(
          SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    delegated_credentials = credentials.with_subject(EMAIL_FROM)
    service = build('gmail', 'v1', credentials=delegated_credentials) 

    message = MIMEText(EMAIL_CONTENT)
    message['to'] = EMAIL_TO
    message['from'] = EMAIL_FROM
    message['subject'] = EMAIL_SUBJECT
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    
    message = (service.users().messages().send(userId='me', body=body)
               .execute())
    print('Message Id: %s' % message['id'])


if __name__ == '__main__':
    main()