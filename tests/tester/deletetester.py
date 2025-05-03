import os
import sys
import logging
from .basetester import BaseTester

class DeleteTester(BaseTester):
    def __init__(self, filename='newtest.txt'):
        super().__init__()
        self._filename = filename

    def run(self):
        logger = logging.getLogger(__name__)
        logger.debug(self._gdrivemanager.deleteFile(self._filename))

        return True