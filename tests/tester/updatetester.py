import os
import sys
from .basetester import BaseTester

class UpdateTester(BaseTester):
    def __init__(self, filename='test.txt', filepath=os.path.abspath(os.path.join(sys.path[0], 'secret', 'update.txt')), metadata=None):
        super().__init__()
        self._filename = filename
        files = self._gdrivemanager.searchFile(f"name='{filename}'")
        self._fileId = files[0]['id']
        self._filepath = filepath
        self._metadata = metadata

    def run(self):
        return self._gdrivemanager.updateFile(self._fileId, self._filepath, self._metadata)