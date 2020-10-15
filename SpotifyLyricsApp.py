from Genius import Genius
from SpotifyLyrics import SpotifyLyrics
from SECRETS import *

import tkinter as tk
import tkinter.scrolledtext as st

class SpotifyLyricsApp():
    def __init__(self, spotify):

        self._spotify = spotify

        self._rootWindow = tk.Tk()

        self._rootWindow.title("Spotify Lyrics Player")

        self._setMinSize()

        self._drawLyricsWindow()

        self._drawSongInfo()

        self._drawRefreshButton()

    def run(self):
        self._rootWindow.mainloop()

    def _setMinSize(self):
        self._rootWindow.minsize(460, 600)

    def _drawRefreshButton(self):
        refreshButton = tk.Button(
            master = self._rootWindow, text = "Refresh Lyrics",
            font = ('Times New Roman', 20),
            command = lambda: [self._updateLyricsWindow(), self._updateSongInfo()]
        )

        refreshButton.pack(side='bottom', anchor='se')

    def _drawSongInfo(self):
        self._displaySongInfo = tk.Label(
            master = self._rootWindow,
            text = f"{self._spotify.getCurrentArtist()}: {self._spotify.getCurrentSongName()}", 
            font = ("Times New Roman", 20))

        self._displaySongInfo.pack(side='bottom', anchor='se')

    def _drawLyricsWindow(self):
        #IMPLEMENT: Center lyrics in window.
        self._lyricsWindow = st.ScrolledText(self._rootWindow, 
                                    width = 52,  
                                    height = 30,  
                                    font = ("Times New Roman", 15)
                                    ) 
        
        self._lyricsWindow.pack(padx = 10, pady = 10, fill = tk.BOTH, expand = True) 

        self._lyricsWindow.insert(tk.INSERT, "Start playing a song on Spotify, then click the refresh button.")

        self._lyricsWindow.configure(state='disabled')

    def _updateSongInfo(self):
        self._displaySongInfo["text"] = f"{self._spotify.getCurrentArtist()}: {self._spotify.getCurrentSongName()}"

    def _updateLyricsWindow(self):
        self._lyricsWindow.configure(state='normal')
        self._lyricsWindow.delete("1.0", "end")

        self._lyricsWindow.insert(tk.INSERT, self._spotify.getLyrics()) 
        self._lyricsWindow.configure(state='disabled')

if __name__ == "__main__":
    genius = Genius(GENIUS_TOKEN)

    spotifyLyrics = SpotifyLyrics(SPOTIFY_CLIENTID, SPOTIFY_CLIENTSECRET, REDIRECT_URI, SCOPES, genius)

    SpotifyLyricsApp(spotifyLyrics).run()
