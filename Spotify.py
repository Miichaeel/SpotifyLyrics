import base64
import requests
import six
import urllib
import webbrowser

class SpotifyScopeError(Exception):
    pass

class Spotify():
    def __init__(self, clientID, clientSecret, redirectURI, scope):
        redirectedURL = self._authUser(clientID, redirectURI, scope)
        authCode = self._getAuthCode(redirectedURL)

        self._clientID = clientID
        self._clientSecret = clientSecret
        self._token, self._refreshToken = self._getTokens(redirectURI, authCode)
        self._headers = self._buildHeaders(self._token)
        self._scopes = scope.split()

    def getRefreshToken(self):
        return self._refreshToken

    def getAccessToken(self, url):
        return self._token

    def refreshAccessToken(self):
        url = "https://accounts.spotify.com/api/token"

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self._refreshToken
        }

        client_creds = base64.b64encode(six.text_type(self._clientID 
                            + ":" 
                            + self._clientSecret).encode("ascii"))
        
        header = {'Authorization': f"Basic {client_creds.decode('ascii')}"
                }

        req = requests.post(url, data=payload, headers=header)

        self._token = req.json()["access_token"]
        self._headers = self._buildHeaders(self._token)

        #Return value?

    def getCurrentSongInfo(self):
        if ("user-read-currently-playing" not in self._scopes or
            "user-read-playback-state" not in self._scopes):
            raise SpotifyScopeError()

        url = "https://api.spotify.com/v1/me/player/currently-playing"
        
        req = requests.get(url, headers=self._headers)

        songInfo = {
            "name": "Unknown",
            "artist": "Unknown",
            "album": "Unknown",
            "release_date": "Unknown",
            }

        if req.status_code == 200 and req.json()["item"]:
            item = req.json()["item"]
       
            songInfo["name"] = item["name"]
                         
            songInfo["artist"] = item["artists"][0]["name"]
                            
            songInfo["album"] = item["album"]["name"]

            songInfo["release_date"] = item["album"]["release_date"]
        
        return songInfo

    def getCurrentArtist(self):
        songInfo = self.getCurrentSongInfo()

        return songInfo["artist"]

    def getCurrentSongName(self):
        songInfo = self.getCurrentSongInfo()

        return songInfo["name"]

    def getCurrentAlbum(self):
        songInfo = self.getCurrentSongInfo()

        return songInfo["album"]

    def getCurrentSongReleaseDate(self):
        songInfo = self.getCurrentSongInfo()

        return songInfo["release_date"]

    def pause(self):
        return self._modifyPlayback("pause", "PUT")

    def play(self):
        return self._modifyPlayback("play", "PUT")

    def nextTrack(self):
        return self._modifyPlayback("next", "POST")

    def prevTrack(self):
        return self._modifyPlayback("previous", "POST")

    def isSongPlaying(self):
        req = self._getPlayback()

        if req.status_code != 200:
            return "A song must be currently playing."

        playing = req.json()["is_playing"]

        return playing

    def toggleShuffle(self, state: bool):
        if type(state) != bool:
            raise ValueError("Value must be a boolean.")
        
        state = f"{state}".lower()

        params = {"state": state}
        
        return self._modifyPlayback("shuffle", "PUT", params)

    def getShuffleState(self):
        req = self._getPlayback()

        if req.status_code != 200:
            return "A song must be currently playing."

        shuffleState = req.json()["shuffle_state"]

        if shuffleState:
            return "Shuffle on."

        return "Shuffle off."

    def setRepeatMode(self, state: str):
        if state not in {"track", "context", "off"}:
            raise ValueError("Value must be 'track,' 'context,' or 'off'.")

        params = {"state": state}

        return self._modifyPlayback("repeat", "PUT", params)

    def getRepeatMode(self):
        req = self._getPlayback()

        if req.status_code != 200:
            return "A song must be currently playing."

        repeatMode = req.json()["repeat_state"]

        return repeatMode.capitalize()

    def seekToPosition(self, positionInSecs: int):
        if type(positionInSecs) != int or positionInSecs < 0:
            raise ValueError("Value must be a positive integer value.")

        params = {"position_ms": positionInSecs * 1000}
        
        return self._modifyPlayback("seek", "PUT", params)

    def getSongPosition(self):
        req = self._getPlayback()

        if req.status_code != 200:
            return "A song must be currently playing."

        songPositionInSecs = req.json()["progress_ms"]

        return songPositionInSecs // 1000

    def setVolume(self, volume: int):
        if type(volume) != int or (volume < 0 or volume > 100):
            raise ValueError("Value must be an integer from 0 to 100 inclusive.")

        params = {"volume_percent": volume}

        return self._modifyPlayback("volume", "PUT", params)

    def getVolume(self):
        req = self._getPlayback()

        if req.status_code != 200:
            return "A song must be currently playing."

        volumePercent = req.json()["device"]["volume_percent"]

        return volumePercent

    def _authUser(self, clientID, redirectURI, scope):
        url = 'https://accounts.spotify.com/authorize'
        
        payload = {
            'client_id': clientID,
            'response_type': 'code',
            'redirect_uri': redirectURI,
            'scope': scope
            }

        req = requests.get(url, params=payload)

        return req.url

    def _getAuthCode(self, url):
        web = webbrowser.open(url)

        url = input("Enter redirected URL: ")

        authCode = urllib.parse.urlparse(url).query[5:]

        return authCode

    def _getTokens(self, redirectURI, authCode):
        payload = {'grant_type': 'authorization_code',
                'code': authCode,
                'redirect_uri': redirectURI}
        
        url = 'https://accounts.spotify.com/api/token'

        client_creds = base64.b64encode(six.text_type(self._clientID 
                            + ":" 
                            + self._clientSecret).encode("ascii"))
        
        header = {'Authorization': f"Basic {client_creds.decode('ascii')}"
                }

        req = requests.post(url, data=payload, headers=header)

        #FIXME: Throw exception if invalid request.

        return req.json()['access_token'], req.json()['refresh_token']

    def _buildHeaders(self, token):
        headers = {"Authorization": f"Bearer {token}"}

        return headers

    def _getPlayback(self):
        if "user-read-playback-state" not in self._scopes:
            raise SpotifyScopeError()

        url = "https://api.spotify.com/v1/me/player"

        req = requests.get(url, headers=self._headers)

        return req

    def _modifyPlayback(self, endpoint, method, params=""):
        if "user-modify-playback-state" not in self._scopes:
                    raise SpotifyScopeError()
                
        url = f"https://api.spotify.com/v1/me/player/{endpoint}"

        if method == "POST":
            req = requests.post(url, params=params, headers=self._headers)
        elif method == "PUT":
            req = requests.put(url, params=params, headers=self._headers)

        return True if req.status_code == 204 else False

