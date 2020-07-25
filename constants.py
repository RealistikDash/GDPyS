# ok so here are the enums for the new priv system
# rather than what cvolton does now, GDPyS will use bitwise privileges similar to RealistikOsu

UserLogIn = 2 << 0
UserPostAccComment =  2 << 1
UserPostComment = 2<<2
UserUploadLevel = 2 << 3
ModRateLevel = 2 << 4
ModRateDemon = 2 << 5
ModRegularBadge = 2 << 6
ModElderBadge = 2 << 7
ClaimDailyChest = 2 << 8
CommandSetAcc = 2 << 9
CommandRename = 2 << 10
ModReqMod = 2 << 11
ModSuggestLevel = 2 << 12
ModBanUser = 2 << 13
ModSetDaily = 2 << 14

__version__ = "InDev"
