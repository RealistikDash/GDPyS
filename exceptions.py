#simple exceptions so they can be handled accordingly

class BannedSongException(Exception):
    pass

class SongNotFoundException(Exception):
    pass
