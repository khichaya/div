from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request  # Updated import for Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import os
import time

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Base folder where attachments will be saved
base_folder = "dd"  # Replace with the path where the folders will be created

def get_gmail_service():
    """Authenticate and get the Gmail API service."""
    creds = None
    try:
        # The file token.json stores the user's access and refresh tokens
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())  # Updated to use Request() correctly
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Error occurred during authentication: {e}")
        return None

def save_attachment(service, message_id, part, email_address):
    """Save the attachment from a message part in a folder named after the sender's email."""
    try:
        if part['filename']:
            # Create a folder based on the sender's email address
            email_folder = os.path.join(base_folder, email_address)
            if not os.path.exists(email_folder):
                os.makedirs(email_folder)

            attachment_id = part['body']['attachmentId']
            attachment = service.users().messages().attachments().get(userId='me', messageId=message_id, id=attachment_id).execute()
            file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
            path = os.path.join(email_folder, part['filename'])
            with open(path, 'wb') as f:
                f.write(file_data)
            print(f"Attachment {part['filename']} saved in folder {email_folder}")
    except Exception as e:
        print(f"Error saving attachment {part['filename']}: {e}")

def list_messages_with_attachments(service, query):
    """List all messages with attachments."""
    try:
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        for message in messages:
            try:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload']['headers']
                email_address = None
                for header in headers:
                    if header['name'] == 'From':
                        email_address = header['value'].split('<')[-1].replace('>', '').strip()

                if email_address:
                    for part in msg['payload']['parts']:
                        if part['filename'] and 'attachmentId' in part['body']:
                            save_attachment(service, msg['id'], part, email_address)
            except Exception as e:
                print(f"Error fetching message {message['id']}: {e}")
                time.sleep(5)  # Optionally, add a delay to retry after a short wait.
    except Exception as e:
        print(f"Error listing messages with query {query}: {e}")

if __name__ == '__main__':
    try:
        service = get_gmail_service()
        if service:
            # Modify the query to search for emails after a specific date
            list_messages_with_attachments(service, query="after:2024/10/14")
    except Exception as e:
        print(f"An error occurred: {e}")
