from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

# Define the scope for Google Drive API access
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Path to the service account JSON file
SERVICE_ACCOUNT_FILE = ''

# Google Drive folder ID where the files should be uploaded
FOLDER_ID = os.getenv('FOLDER_ID')

def upload_to_drive(logs_filename, code_logs_filename):
    filenames = [logs_filename, code_logs_filename]

    # Use service account credentials to authenticate
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Step 2: Build the Google Drive API service using the valid credentials
    service = build('drive', 'v3', credentials=creds)

    # Step 3: Delete all existing files in the folder before uploading new ones
    try:
        query = f"'{FOLDER_ID}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if items:
            for item in items:
                file_id = item['id']
                print(f"Deleting file with ID: {file_id}")
                service.files().delete(fileId=file_id).execute()
            print(f"All files in folder ID {FOLDER_ID} deleted successfully.")
        else:
            print(f"No files found in folder ID {FOLDER_ID}.")

    except Exception as e:
        print(f"Error deleting files: {e}")
        return

    # Step 4: Upload new files to the folder
    for filename in filenames:
        # Ensure the file exists locally before attempting to upload
        if not os.path.exists(filename):
            print(f"File {filename} not found locally. Skipping upload.")
            continue

        # Set metadata for the file, such as its name and parent folder
        file_metadata = {
            'name': filename,
            'parents': [FOLDER_ID]  # Specify the parent folder
        }

        # Specify the file to upload and its mimetype (CSV in this case)
        media = MediaFileUpload(filename, mimetype='text/csv')

        # Upload the file to Google Drive
        try:
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"File {filename} uploaded to Google Drive with file ID: {file.get('id')}")
        except Exception as e:
            print(f"Error uploading file {filename}: {e}")

