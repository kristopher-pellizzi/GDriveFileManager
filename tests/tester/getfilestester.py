from .basetester import BaseTester

class GetFilesTester(BaseTester):
    def run(self):
        return self._gdrivemanager.getFilesList()