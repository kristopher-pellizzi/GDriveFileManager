from .basetester import BaseTester

class GetFilesTester(BaseTester):
    def run(self):
        print(self._gdrivemanager.getFilesList())

        return True