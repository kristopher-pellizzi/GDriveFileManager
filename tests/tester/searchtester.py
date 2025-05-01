from .basetester import BaseTester

class SearchTester(BaseTester):
    def __init__(self, filename = 'test.txt'):
        super().__init__()
        self._filename = filename

    def set_search_filename(self, name):
        self._filename = name

    def run(self):
        print(f"Searching for {self._filename}")
        return self._gdrivemanager.searchFile(f"name='{self._filename}'")
