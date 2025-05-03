import os
import sys
import logging
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
        if parentName is not None:
            files = self._gdrivemanager.searchFile(f"name='{parentName}'")
            self._parentFileId = files[0]['id']
        else:
            self._parentFileId = None
        self._additionalMetadata = additionalMetadata

    def run(self):
        logger = logging.getLogger(__name__)
        logger.debug(self._gdrivemanager.createFile(self._filepath, self._filename, self._parentFileId, self._additionalMetadata))

        return True