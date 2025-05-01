import os
import sys
from .basetester import BaseTester

class DeleteTester(BaseTester):
    def __init__(self, filename='newtest.txt'):
        super().__init__()
        self._filename = filename

    def run(self):
        return self._gdrivemanager.deleteFile(self._filename)