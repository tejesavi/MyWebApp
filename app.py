from flask import Flask, request, render_template, redirect, url_for
from azure.storage.blob import BlobServiceClient
from azure.storage.fileshare import ShareFileClient
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Azure Storage settings
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
FILE_SHARE_NAME = os.getenv("FILE_SHARE_NAME")

# Initialize Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    try:
        # Upload to Blob Storage
        blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=file.filename)
        blob_client.upload_blob(file, overwrite=True)  # Use overwrite=True to replace existing blobs

        # Upload to Azure File Share
        file_client = ShareFileClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING, 
                                                              share_name=FILE_SHARE_NAME, 
                                                              file_path=file.filename)

        # Read the file content for uploading to Azure File Share
        file_stream = file.read()  # Read the content of the file
        file_client.upload_file(file_stream)  # Upload file content to Azure Files

    except Exception as e:
        return f"An error occurred: {str(e)}", 500

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
