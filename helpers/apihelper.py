import aiohttp
from objects.songs import Song
from exceptions import BannedSongException, SongNotFoundException
from constants import Secrets
import logging


class BoomlingsAPI():
    """A wrapper around the boomlings servers."""

    def __init__(self, server_url: str = "http://www.boomlings.com/database/"):
        """Inits the Boomlings API."""
        self.URL = server_url

    async def get_boomlings_song(self, song_id: int) -> Song:
        """Requests a song from Boomlings and returns a song object."""
        async with aiohttp.ClientSession() as session:
            async with session.post(self.URL + "getGJSongInfo.php", data={
                "songID": song_id,
                "secret": Secrets.normal
            }) as resp:
                response = await resp.text()
        logging.debug(response)
        # I am not sure what causes an empty response but I am certain it exists.
        if response in ("-1", ""):
            raise SongNotFoundException
        if response == "-2":
            raise BannedSongException

        song = response.split("|")
        return Song(
            int(song[1][1:-1]),
            song[3][1:-1],
            int(song[5][1:-1]),
            song[7][1:-1],
            float(song[9][1:-1]),
            song[13][1:-1],
            False
        )
