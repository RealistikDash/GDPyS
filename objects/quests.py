from dataclasses import dataclass

@dataclass
class Quest():
    """The quest object."""
    sort : int # I wanted to call it type but thats a python reserver thing
    text : str
    amount : int
