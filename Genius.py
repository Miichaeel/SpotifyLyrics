import requests

BASE_URL = "http://api.genius.com/"

class GeniusTokenError(Exception):
    pass

class Genius():
    def __init__(self, clientToken):
        self.headers = self._buildHeaders(clientToken)

    def _buildHeaders(self, token):
        headers = {"Authorization": f"Bearer {token}"}

        url = BASE_URL + "search/?"

        req = requests.get(url, headers=headers)

        if "error" in req.json():
            raise GeniusTokenError(req.json()["error_description"])
        
        return headers
        
    def searchSong(self, search: str):
        url = BASE_URL + "search/?"
        
        params = {'q': search}
        
        req = requests.get(url, params=params, headers=self.headers)

        if req.status_code == 200 and req.json()["response"]["hits"]:
            return req.json()["response"]["hits"]

        return []

    def getSongURL(self, search: str) -> str:
        songURL = self.searchSong(search)

        if songURL:
            songURL = songURL[0]["result"]["url"]

        return songURL

