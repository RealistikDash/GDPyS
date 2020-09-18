# My own rate limiting module. Probably not how it should be done but this suits my needs perfectly
from helpers.generalhelper import dict_keys
from helpers.timehelper import get_timestamp
import logging

class RateLimit():
    """Handles rate limiting."""
    def __init__(self):
        self.struct = {"timestamp" : 0} # The struct of every ip.
        self.ips = {} # List of structs with ips
        self.limits = {}
    
    def update_struct(self):
        """Updates struct for all cached IPs (may be costly)."""
        logging.debug("Updating all ip rate limits with new struct")
        all_ips = dict_keys(self.ips)
        structs_list = dict_keys(self.struct)
        for ip in all_ips:
            for struct in structs_list:
                if struct not in dict_keys(self.ips[ip]):
                    self.ips[ip][struct] = self.struct[struct]
    
    def add_to_struct(self, name : str, default : int = 0, limit : int = 0):
        """"Appends onto the struct."""
        self.struct[name] = default
        self.limits[name] = limit
        logging.debug(f"Added {name} to struct with default value of {default} and limit of {limit}")
        self.update_struct()
    
    def bump_and_check(self, ip : str, name : str) -> bool:
        """Bumps a value for an ip and checks if it reached the limit. Returns bool."""
        logging.debug("Bumping ip count")
        if ip not in dict_keys(self.ips):
            logging.debug("New IP.")
            self.ips[ip] = self.struct
            self.ips[ip]["timestamp"] = get_timestamp() # Messy
        
        # Checks to reset counts
        if self.ips[ip]["timestamp"] + 86400 < get_timestamp():
            logging.debug("Count expired for ip. Reseting.")
            self.ips[ip] = self.struct
            self.ips[ip]["timestamp"] = get_timestamp() # Messy

        self.ips[ip][name] += 1

        # Check if it passed the limit
        if self.limits[name] < self.ips[ip][name]:
            logging.debug(f"{ip} reached limit for {name}")
            return False
        logging.debug(f"{ip} passed limit with {self.ips[ip][name]}/{self.limits[name]}")
        return True

# Global rate limiter
rate_limiter = RateLimit()
