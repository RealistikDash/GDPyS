

class IPLimit():
    """Limit actions per ip per user"""
    def __init__(self):
        self.ips = {}
        self.default_struct = {
            "Register" : 0,
            "Login" : 0
        }
    
    def bump_ip(self, ip : str, action : str):
        """Rises the action count"""
        if ip not in list(self.ips.keys()):
            self.ips[ip] = self.default_struct
        
        self.ips[ip][action] += 1

    def get_action_count(self,ip: str, action: str) -> int:
        """Returns action count for ip"""
        return self.ips[ip][action]
