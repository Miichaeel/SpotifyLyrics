from bs4 import BeautifulSoup
from Genius import Genius
from Spotify import Spotify

import requests

class SpotifyLyrics(Spotify):
    def __init__(self, clientID, clientSecret, redirectURI, scope, genius: Genius):
        super().__init__(clientID, clientSecret, redirectURI, scope)
        self._genius = genius

    def getLyrics(self):
        if self.isSongPlaying():

            lyrics = "Unable to find current song lyrics."

            songInfo = self.getCurrentSongInfo()

            songSearch = f"{songInfo['artist']} {songInfo['name']}"

            lyricsURL = self._genius.getSongURL(songSearch)

            if lyricsURL:
                lyrics = self._parseLyrics(lyricsURL)

            return lyrics

        return "A song is not currently playing."
        
    def _parseLyrics(self, url):
        page = requests.get(url)

        soup = BeautifulSoup(page.content, "html.parser")

        lyrics = soup.find(class_="lyrics").get_text()

        return lyrics
