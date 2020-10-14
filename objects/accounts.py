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
    demons : int
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
    youtube : str
    twitter : str
    twitch : str
    state_req : bool
    state_msg : bool
    state_comment : bool

@dataclass
class AccountExtras():
    """Extra account information that may not be always needed."""
    count_reqs : int
    count_messages : int
    count_new_friends : int
    friend_requests : list
    sent_requests : list
    received_requests : list

@dataclass
class FriendRequest():
    """Dataclass storing friend request info."""
    id : int
    account_id : int
    target_id : int
    content_base64 : str
    content : str
    timestamp : int
    new : bool
