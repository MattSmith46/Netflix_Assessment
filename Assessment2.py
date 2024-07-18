import os
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Function to authenticate and build the service
def authenticate():
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

# Function to get all child objects recursively
def get_child_objects(service, folder_id):
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])
    
    child_objects_count = 0
    nested_folders_count = 0
    
    for item in items:
        child_objects_count += 1
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            nested_folders_count += 1
            sub_child_objects, sub_nested_folders = get_child_objects(service, item['id'])
            child_objects_count += sub_child_objects
            nested_folders_count += sub_nested_folders
    
    return child_objects_count, nested_folders_count

# Function to generate the report
def generate_report(service, source_folder_id):
    query = f"'{source_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    top_level_folders = results.get('files', [])
    
    report = []
    total_nested_folders = 0
    
    for folder in top_level_folders:
        child_objects_count, nested_folders_count = get_child_objects(service, folder['id'])
        report.append({
            'Folder Name': folder['name'],
            'Folder ID': folder['id'],
            'Total Files': child_objects_count,
            'Total Nested Folders': nested_folders_count
        })
    
    return report

def main():
    source_folder_id = '1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V'
    service = authenticate()
    report = generate_report(service, source_folder_id)
    
    with open('Assessment2.json', 'w') as outfile:
        json.dump(report, outfile, indent=4)
    
    print("Report saved to Assessment2.json")

if __name__ == '__main__':
    main()
    