from __future__ import print_function
import os.path
import json
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def authenticate():

    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'Netflix_Assessment.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def count_child_objects(service, folder_id):
    total_files = 0
    total_folders = 0

    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, mimeType)").execute()
    items = results.get('files', [])

    for item in items:
        total_files += 1
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            total_folders += 1
            child_files, child_folders = count_child_objects(service, item['id'])
            total_files += child_files
            total_folders += child_folders

    return total_files, total_folders

def generate_report(service, source_folder_id):
    report = {}
    query = f"'{source_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    total_nested_folders = 0

    for item in items:
        folder_id = item['id']
        folder_name = item['name']
        total_files, total_folders = count_child_objects(service, folder_id)
        report[folder_name] = {
            'total_files': total_files,
            'total_folders': total_folders
        }
        total_nested_folders += total_folders

    report['total_nested_folders'] = total_nested_folders
    return report

def write_report_to_json(report, filename='Assessment2.json'):
    with open(filename, 'w') as report_file:
        json.dump(report, report_file, indent=4)

def generate_and_write_report(source_folder_id, json_filename='Assessment2.json'):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    report = generate_report(service, source_folder_id)
    write_report_to_json(report, json_filename)

if __name__ == '__main__':
    source_folder_id = '1cpo-7jgKSMdde-QrEJGkGxN1QvYdzP9V'
    generate_and_write_report(source_folder_id)
