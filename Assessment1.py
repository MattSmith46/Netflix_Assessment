import os
import pickle
import json
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

def generate_drive_report(folder_id, output_file):
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
        
        report = {
            "folder_id": folder_id,
            "num_files": num_files,
            "num_folders": num_folders
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=4)
        
        return f"Report saved to {output_file}"
    except HttpError as error:
        error_report = {"error": str(error)}
        with open(output_file, 'w') as f:
            json.dump(error_report, f, indent=4)
        return f"An error occurred: {error}"

# Generate Report
folder_id = '1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V'
output_file = 'Assessment1.json'
message = generate_drive_report(folder_id, output_file)
print(message)
