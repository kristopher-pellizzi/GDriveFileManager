from .basetester import BaseTester

class GetFileTester(BaseTester):
    def __init__(self, filename='test.txt'):
        super().__init__()
        self._filename = filename
        files = self._gdrivemanager.searchFile(f"name='{filename}'")
        self._fileId = files[0]['id']

    def run(self):
        print(self._gdrivemanager.getFile(self._fileId))

        return True