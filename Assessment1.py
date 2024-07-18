import os
import pickle
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def authenticate_gdrive():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'Netflix_Assessment.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def generate_drive_report(folder_id):
    creds = authenticate_gdrive()
    
    try:
        service = build('drive', 'v3', credentials=creds)
        
        num_files = 0
        num_folders = 0
        
        query = f"'{folder_id}' in parents and trashed = false"
        
        results = service.files().list(q=query, 
                                       spaces='drive', 
                                       fields='nextPageToken, files(id, name, mimeType)').execute()
        items = results.get('files', [])
        
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                num_folders += 1
            else:
                num_files += 1
        
        report = (
            f"Report for folder ID '{folder_id}':\n"
            f"Total number of files: {num_files}\n"
            f"Total number of folders: {num_folders}\n"
        )
        
        return report
    except HttpError as error:
        return f"An error occurred: {error}"

# Example usage
folder_id = '1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V'
report = generate_drive_report(folder_id)
print(report)
