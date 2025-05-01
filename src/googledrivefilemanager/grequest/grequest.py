import requests as reqs

class GRequest(object):

    expired_token_reason = 'ACCESS_TOKEN_EXPIRED'

    def __init__(self, method, url, headers = None, data = None, files = None, json = None, stream = False):
        self._method = method
        self._url = url
        self._headers = headers
        self._data = data
        self._files = files
        self._json = json
        self._stream = stream


    def updateHeader(self, headerName, newValue):
        self._headers[headerName] = newValue


    def run(self):
        res = reqs.request(self._method, self._url, headers = self._headers, data = self._data, files = self._files, json = self._json, stream = self._stream)

        if res.status_code != 401:
            return res

        # If response status code is 401 check whether it is due to an expired access token.
        # In that case, return the expired_token_reason string, so that the GDrive File Manager knows that it has to refresh the access_token

        res = res.json()

        if 'error' not in res:
            return res

        if 'details' not in res['error']:
            return res

        if 'reason' not in res['error']['details'][0]:
            return res

        reason = res['error']['details'][0]['reason']

        if reason != GRequest.expired_token_reason:
            return res

        return reason