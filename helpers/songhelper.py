from objects.songs import Song
from constants import ResponseCodes
from conn.mysql import myconn
import logging

class SongHelper():
    """Helper class that helps with songs. Good desc."""
    async def __init__(self):
        """Inits the song helper."""
        self.song_obj_cache = {}
        self.top_artists = await self._top_artists()
    
    async def _top_artists(self) -> list:
        """Returns a list of top artists names."""
        with myconn.conn.cursor() as mycursor:
            await mycursor.execute("SELECT authorName AS frequency FROM songs GROUP BY authorName ORDER BY frequency DESC")
            authors = await mycursor.fetchall()
        
        artists = []
        for artist in authors:
            artists.append(artist[0])
        
        return artists

songs = SongHelper()