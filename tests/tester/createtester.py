import os
import sys
from .basetester import BaseTester

class CreateTester(BaseTester):
    def __init__(
            self, 
            filepath=os.path.abspath(os.path.join(sys.path[0], 'secret', 'test.txt')), 
            filename='newtest.txt', 
            parentName='GDriveFileManagerTests', 
            additionalMetadata=None):
        
        super().__init__()
        self._filepath = filepath
        self._filename = filename
        files = self._gdrivemanager.searchFile(f"name='{parentName}'")
        self._parentFileId = files[0]['id']
        self._additionalMetadata = additionalMetadata

    def run(self):
        print(self._gdrivemanager.createFile(self._filepath, self._filename, self._parentFileId, self._additionalMetadata))

        return True