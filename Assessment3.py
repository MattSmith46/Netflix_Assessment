import os
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_gdrive():
    creds = service_account.Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service

def extract_folder_id_from_url(url):
    patterns = [
        r'drive/folders/([a-zA-Z0-9_-]+)',  # Matches the usual folder URL pattern
        r'folders/([a-zA-Z0-9_-]+)',  # Matches if only the folders path is provided
        r'id=([a-zA-Z0-9_-]+)'  # Matches if the folder ID is provided as a query parameter
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError('Invalid Google Drive folder URL')

def copy_file(service, file_id, dest_folder_id):
    """Copies a file to the destination folder."""
    file = service.files().get(fileId=file_id, fields='name, mimeType').execute()
    copied_file = {
        'name': file['name'],
        'parents': [dest_folder_id]
    }
    return service.files().copy(fileId=file_id, body=copied_file).execute()

def copy_folder(service, folder_id, dest_folder_id):
    folder = service.files().get(fileId=folder_id, fields='name').execute()
    copied_folder = {
        'name': folder['name'],
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [dest_folder_id]
    }
    new_folder = service.files().create(body=copied_folder, fields='id').execute()
    copy_contents(service, folder_id, new_folder['id'])

def copy_contents(service, src_folder_id, dest_folder_id):
    query = f"'{src_folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields='files(id, name, mimeType)').execute()
    items = results.get('files', [])

    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            copy_folder(service, item['id'], dest_folder_id)
        else:
            copy_file(service, item['id'], dest_folder_id)

def main():
    service = authenticate_gdrive()
    src_folder_id = '1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V'
    dest_folder_url = 'https://drive.google.com/drive/u/1/folders/1Q0lhO5n5o6LoySlZJttMdSmFqSR5Wwr9'
    dest_folder_id = extract_folder_id_from_url(dest_folder_url)
    copy_contents(service, src_folder_id, dest_folder_id)
    print("Contents copied successfully.")

if __name__ == '__main__':
    main()
