from dataclasses import dataclass

@dataclass
class RGB:
    """Dataclass representation of an RGB colour value."""

    red: int = 0
    green: int = 0
    blue: int = 0
    
    def __str__(self):
        """Retuns a string representation of the RGB value."""

        return f"{self.red},{self.green},{self.blue}"
    
    def __repr__(self):
        """Debugging representation of the RGB value."""

        return f"<RGB({self.red}, {self.green}, {self.blue})>"
    
    def api(self) -> list:
        """Converts the object into a list for api reasons."""

        return [self.red, self.green, self.blue]
    
    @classmethod
    def from_string(cls, string: str):
        """Creates an instance of `RGB` from a comma separated string of RGB
        values.
        
        Args:
            string (str): A string of RGB ints in the order of red, green,
                blue.
        """

        # First we clean up the string in case.
        string = string.replace(" ", "")

        # Now we split it and assign it.
        (
            red,
            green,
            blue
        ) = string.split(",")

        return cls(
            int(red),
            int(green),
            int(blue)
        )
