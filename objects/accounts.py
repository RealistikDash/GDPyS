from dataclasses import dataclass

@dataclass
class Account():
    """Account struct."""
    username : str
    email : str
    account_id : int
    user_id : int
    register_date : int
    privileges : int
    stars : int
    icon : int
    colour1 : int
    colour2 : int
    icon_type : int
    coins : int
    user_coins : int
    ship : int
    ball : int
    ufo : int
    wave : int
    robot : int
    glow : bool
    cp : int
    diamonds : int
    orbs : int
    spider : int
    explosion : int
    banned : bool
    acc_comments : list
