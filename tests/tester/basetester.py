import os
import sys
from googledrivefilemanager import GoogleDriveFileManager

class BaseTester(object):
    def __init__(self):
        self._gdrive_folder_name = "GDriveFileManagerTests"
        self._saDirPath = os.path.abspath(os.path.join(sys.path[0], 'secret'))
        self._saFilename = "service_account.json"
        self._gdrivemanager = GoogleDriveFileManager(self._saDirPath, self._saFilename)


    def run(self):
        pass