

class Plugin:
    def __init__(self):
        self.name = ""
        self.author = ""
        self.description = ""
        self.version = ""

    @property
    def metadata(self):
        return {"name": self.name, "author": self.author, "description": self.description, "version": self.version}