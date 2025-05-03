import logging
from .basetester import BaseTester

class GetFilesTester(BaseTester):
    def run(self):
        logger = logging.getLogger(__name__)
        logger.debug(self._gdrivemanager.getFilesList())

        return True