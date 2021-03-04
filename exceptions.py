# Custom GDPyS Exceptions
class GDPySHandlerException(Exception):
    """A Geometry Dash response error. Called when an error code is to be
    sent to the client."""
    pass

class GDPySAlreadyExists(Exception):
    """Error raised when something already exists."""
    pass

class GDPySDoesntExist(Exception):
    """Error raised when something doesnt exist."""
