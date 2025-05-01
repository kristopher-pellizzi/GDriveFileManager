import os
import sys
from .basetester import BaseTester

class DownloadTester(BaseTester):
    def __init__(self, filename='test.txt', outputPath=os.path.abspath(os.path.join(sys.path[0], 'secret', 'test.txt'))):
        super().__init__()
        self._filename = filename
        self._outPath = outputPath

    def run(self):
        print(self._gdrivemanager.downloadFile(self._filename, self._outPath))

        return True