# simple exceptions so they can be handled accordingly

class BannedSongException(Exception):
    pass


class SongNotFoundException(Exception):
    pass


class GDPySCommandError(Exception):
    """Exception raised by GDPyS commands."""
    pass


class GDPySCommandNotFound(Exception):
    """Exception raised by command helper when no command is found."""
    pass


class GDPySCommandMissingPrivileges(Exception):
    pass


class LangNotFound(Exception):
    """Raised by langhelper if language is not found."""
