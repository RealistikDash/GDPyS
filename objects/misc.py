from dataclasses import dataclass


@dataclass
class RuntimeSettings():
    """GDPyS"""
    no_ascii: bool


@dataclass
class QueryResponse():
    """Small object responsible for storing 2 data values returned by your search."""
    total_results: int
    results: list

# Not sure why I did it but I did it


@dataclass
class RGB():
    """Stores RGB colour values."""
    red: int
    green: int
    blue: int

    def __str__(self):  # So we can just format it in.
        return f"{self.red},{self.green},{self.blue}"


@dataclass
class Privilege():
    """Dataclass for privileges."""
    ID: int
    name: str
    privileges: int
    colour: RGB
