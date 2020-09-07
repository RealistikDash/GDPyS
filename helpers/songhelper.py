from objects.songs import Song
from helpers.apihelper import BoomlingsAPI
from helpers.generalhelper import dict_keys
from constants import ResponseCodes
from conn.mysql import myconn
import logging

class SongHelper():
    """Helper class that helps with songs. Good desc."""
    def __init__(self):
        """Inits the song helper."""
        self.song_obj_cache = {}
        self.top_artists = []
        self.api = BoomlingsAPI()
    
    async def _top_artists(self) -> list:
        """Returns a list of top artists names."""
        with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT authorName AS frequency FROM songs GROUP BY authorName ORDER BY frequency DESC")
            authors = await mycursor.fetchall()
        
        artists = []
        for artist in authors:
            artists.append(artist[0])
        
        return artists
    
    async def add_song_to_db(self, song : Song):
        """Adds a song object to the database."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("INSERT INTO songs (ID, name, authorID, authorName, size, download) VALUES (%s,%s,%s,%s,%s,%s)", (
                song.ID,
                song.name,
                song.author_id,
                song.author_name,
                song.file_size,
                song.url
            ))
            await myconn.conn.commit()
    
    async def _song_from_db(self, song_id : int) -> Song:
        """Gets song object from database."""
        async with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT ID, name, authorID, authorName, size, download, isDisabled FROM songs WHERE ID = %s LIMIT 1", (song_id,))
            song = await mycursor.fetchone()
        if song is None:
            return None
        return Song(
            song[0],
            song[1],
            song[2],
            song[3],
            song[4],
            song[5],
            bool(song[6])
        )
    
    async def _cache_song_obj(self, song_id : int) -> None:
        """Force cache song object."""
        song = await self._song_from_db(song_id)
        if song is None:
            song = await self.add_from_boomlings(song_id)
        self.song_obj_cache[song_id] = song
    
    async def get_song_obj(self, song_id: int) -> Song:
        """Returns a song object of given song id."""
        song_id = int(song_id)
        if song_id not in dict_keys(self.song_obj_cache):
            await self._cache_song_obj(song_id)
        return self.song_obj_cache[song_id]
    
    async def add_from_boomlings(self, song_id : int) -> None:
        """Adds a song from boomlings to database."""
        # TODO : Error handling
        boomlings_song = await self.api.get_boomlings_song(song_id)
        await self.add_song_to_db(boomlings_song)

songs = SongHelper()