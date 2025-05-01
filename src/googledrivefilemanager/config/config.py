# Google Drive File Manager Initialization Config
gdrive_jwt_scope = 'https://www.googleapis.com/auth/drive'
gdrive_jwt_aud = 'https://oauth2.googleapis.com/token'
gdrive_get_token_url = 'https://oauth2.googleapis.com/token'
gdrive_get_token_grant_type = 'urn:ietf:params:oauth:grant-type:jwt-bearer'
gdrive_default_sa_filename = 'gdrivefmanager_service_account.json'

# Methods Config
gdrive_get_files_list_url = 'https://www.googleapis.com/drive/v3/files'
gdrive_search_file_url = 'https://www.googleapis.com/drive/v3/files?q={0}'
gdrive_get_file_url = 'https://www.googleapis.com/drive/v3/files/{0}'
gdrive_get_file_default_fields = "kind,id,name,mimeType,parents"
gdrive_download_file_chunk_size = 1024 * 1024 # 1MB
gdrive_download_file_url = 'https://www.googleapis.com/drive/v3/files/{0}?alt=media'
gdrive_upload_file_chunk_size = 1024 * 1024 # 1MB
gdrive_upload_file_url = 'https://www.googleapis.com/upload/drive/v3/files/{0}?uploadType=resumable'
gdrive_create_file_upload_url = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable' # This URL starts a resumable upload
gdrive_delete_file_url = 'https://www.googleapis.com/drive/v3/files/{0}'