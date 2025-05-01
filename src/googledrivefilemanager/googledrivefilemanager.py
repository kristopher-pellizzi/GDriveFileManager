import os
import jwt
import json
import time
import mimetypes
import requests as reqs
from .grequest import GRequest
from .config import *

class GoogleDriveFileManager(object):
    def _generateJwt(self):
        payload = dict()

        payload['iss'] = self._serviceAccount['client_email']
        payload['scope'] = gdrive_jwt_scope
        payload['aud'] = gdrive_jwt_aud
        now = int(time.time())
        payload['iat'] = now
        payload['exp'] = now + 3600

        private_key = self._serviceAccount['private_key']

        return jwt.encode(payload, key = private_key, algorithm = 'RS256')


    def _getAccessToken(self):
        url = gdrive_get_token_url

        data = {
            'grant_type': gdrive_get_token_grant_type,
            'assertion': self._jwt
        }

        res = reqs.post(url, data = data)

        if res.status_code != 200:
            print("Error while invoking {0} to get the access token".format(url))
            print(res.content)
            exit(1)

        return res.json()['access_token']


    def __init__(self, saDirPath, saFileName = gdrive_default_sa_filename):

        saDirPath = os.path.abspath(saDirPath)

        self._saPath = os.path.join(saDirPath, saFileName)

        with open(self._saPath, "r") as f:
            self._serviceAccount = json.load(f)

        self._jwt = self._generateJwt()

        self._token = self._getAccessToken()


    def _refreshToken(self):
        with open(self._saPath, "r") as f:
            self._serviceAccount = json.load(f)

        self._jwt = self._generateJwt()
        self._token = self._getAccessToken()


    def _makeRequest(self, method, url, headers = None, data = None, files = None, json = None, stream = False):
        reqHeaders = {
            'Authorization': 'Bearer {0}'.format(self._token)
        }

        if headers is not None:
            reqHeaders.update(headers)

        req = GRequest(method, url, headers = reqHeaders, data = data, files = files, json = json, stream = stream)
        res = req.run()

        if res == GRequest.expired_token_reason:
            self._refreshToken()
            req.updateHeader('Authorization', 'Bearer {0}'.format(self._token))
            res = req.run()

        return res


    def getFilesList(self):
        """
            Returns the list of files stored in the Drive, with their fileIds. 
            Note that if more files/folders have the same name, all of them are returned in the list.
            Use the getFilesList method in order to check which is the parent of the returned entities
            to understand which is the correct entry.
            response field nextPageToken is actually ignored, may return a partial result
        """

        url = gdrive_get_files_list_url

        res = self._makeRequest('GET', url)

        if res.status_code != 200:
            print("Error while invoking {0}".format(url))
            print(res.content)
            exit(1)
        
        return res.json()['files']


    def searchFile(self, query):
        """
            Returns the list of files stored in the Drive matching the given query, with their fileIds. 
            Note that if more files/folders have the same name, all of them are returned in the list.
            Use the getFilesList method in order to check which is the parent of the returned entities
            to understand which is the correct entry.
            response field nextPageToken is actually ignored, may return a partial result
        """

        url = gdrive_search_file_url.format(query)

        res = self._makeRequest('GET', url)

        if res.status_code != 200:
            print("Error while invoking {0}".format(url))
            print(res.content)
            exit(1)

        return res.json()['files']


    def getFile(self, fileId, fields=gdrive_get_file_default_fields):
        """
            Get the attributes of the file associated to the given fileId.
            It is possible to override default returned fields.
            Check https://developers.google.com/workspace/drive/api/reference/rest/v3/files#File for more information (fields are the File object fields)
        """

        url = f"{gdrive_get_file_url.format(fileId)}?{fields}"

        res = self._makeRequest('GET', url)

        if res.status_code != 200:
            print("Error while invoking {0}".format(url))
            print(res.content)
            exit(1)

        return res.json()


    def _downloadFile(self, fileId, filePath):
        url = gdrive_download_file_url.format(fileId)

        res = self._makeRequest('GET', url, stream = True)

        if res.status_code != 200:
            print("Error while invoking {0}".format(url))
            print(res.content)
            exit(1)

        with open(filePath, "wb") as f:
            chunkSize = gdrive_download_file_chunk_size

            for chunk in res.iter_content(chunk_size = chunkSize):
                if chunk:
                    f.write(chunk)

        
    def downloadFile(self, filename, outputPath):
        """
            Searches a file by filename and downloads it from Drive into the specified outputPath.
            Note that this method assumes only a single file is returned from the searchFile method.
            If more files exist with the same name, it will download the first entry found in the list returned by searchFile
        """

        queryRes = self.searchFile("name='{0}'".format(filename))

        if len(queryRes) <= 0:
            print("File {0} not found or not shared with the service account in use".format(filename))
            exit(1)

        self._downloadFile(queryRes[0]['id'], outputPath)
        print("File {0} downloaded into {1}".format(filename, os.path.abspath(outputPath)))


    def _resumeUpload(self, fileSize, resumableSessionUri):
        headers = {
            'Content-Range': 'bytes */{0}'.format(fileSize)
        }

        res = self._makeRequest('PUT', resumableSessionUri, headers = headers)

        return res


    def _uploadFile(self, resumableSessionUri, filePath):
        fileSize = os.path.getsize(filePath)
        chunkSize = gdrive_upload_file_chunk_size
        contentType = mimetypes.guess_type(filePath)[0]

        if contentType is None:
            contentType = 'application/octet-stream'

        headers = {
            'Content-Type': contentType,
            'Content-Length': str(chunkSize)
        }

        uploadRange = '0-{0}/{1}'.format(chunkSize - 1, fileSize)
        uploadFinished = False

        while not uploadFinished:
            rangeStart, rangeEnd = map(int, uploadRange.split('/')[0].split('-'))

            with open(filePath, "rb") as f:
                f.seek(rangeStart, 0)
                chunk = f.read(chunkSize)
                data = chunk
                currentChunkSize = f.seek(0, 1) - rangeStart

            if currentChunkSize < chunkSize:
                headers['Content-Length'] = str(currentChunkSize)
                uploadRange = '{0}-{1}/{2}'.format(rangeStart, rangeStart + currentChunkSize - 1, fileSize)

            print("Uploading bytes {0}".format(uploadRange))
            headers['Content-Range'] = 'bytes {0}'.format(uploadRange)

            res = self._makeRequest('PUT', resumableSessionUri, headers = headers, data = data)
            res = reqs.put(resumableSessionUri, headers = headers, data = data)

            if str(res.status_code).startswith('4') and res.status_code != 404:
                print("Request error")
                print(res.content)
                exit(1)

            if str(res.status_code).startswith('5'):
                print("Upload error. Trying to resume upload")
                res = self._resumeUpload(fileSize, resumableSessionUri)

            if res.status_code == 404:
                print("Upload session expired. Upload must be restarted from the beginning")
                return False

            if 'Range' in res.headers:
                resRange = res.headers['Range'].split('=')[1]
                rangeStart, rangeEnd = map(int, resRange.split('-'))
            else:
                # No header "Range" found => no bytes have been received from server or upload is completed
                rangeEnd = -1

            uploadRange = '{0}-{1}/{2}'.format(rangeEnd + 1, rangeEnd + chunkSize, fileSize)

            if res.status_code == 200 or res.status_code == 201:
                uploadFinished = True

        return True


    def updateFile(self, fileId, filePath, metaData = None):
        """
            Updates an existing file's content and/or metadata.
        """

        url = gdrive_upload_file_url.format(fileId)

        init_res = self._makeRequest('PATCH', url, json = metaData)

        if init_res.status_code != 200:
            print("Error while invoking initial request url: {0}".format(url))
            print(init_res.content)
            exit(1)

        resumableSessionUri = init_res.headers['Location']

        return self._uploadFile(resumableSessionUri, filePath)


    def createFile(self, filePath, filename, parentFileId, additionalMetadata=None):
        """
            Creates a new file, with the content of filePath and the specified metadata, if any.
            This method implements a resumable upload.
            More info at https://developers.google.com/workspace/drive/api/reference/rest/v3/files/update
        """

        url = gdrive_create_file_upload_url
        
        metaData = additionalMetadata if additionalMetadata is not None else dict()
        metaData.update({'name': filename, 'parents': [parentFileId]})

        init_res = self._makeRequest('POST', url, json = metaData)

        if init_res.status_code != 200:
            print("Error while invoking initial request url: {0}".format(url))
            print(init_res.content)
            exit(1)

        resumableSessionUri = init_res.headers['Location']

        return self._uploadFile(resumableSessionUri, filePath)


    def _deleteFile(self, fileId):
        url = gdrive_delete_file_url.format(fileId)

        res = self._makeRequest('DELETE', url)

        if not str(res.status_code).startswith('2'):
            print("Error while invoking {0}".format(url))
            print(res.content)
            exit(1)


    def deleteFile(self, fileName):
        """
            Delete an existing file by filename.
            Note that this method assumes only a single file is returned from the searchFile method.
            If more files exist with the same name, it will delete the first entry found in the list returned by searchFile.
            WARNING: with the limitation mentioned above, this method may delete the wrong file/folder.
            USE IT AT YOUR OWN RISK
        """

        files = self.searchFile("name='{0}'".format(fileName))

        if len(files) <= 0:
            print("File {0} not found".format(fileName))
            return

        fileId = files[0]['id']
        self._deleteFile(fileId)