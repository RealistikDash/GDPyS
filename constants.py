# ok so here are the enums for the new priv system
# rather than what cvolton does now, GDPyS will use bitwise privileges similar to RealistikOsu

UserLogIn = 2 << 0
UserPostAccComment =  2 << 1
UserPostComment = 2 << 2
UserUploadLevel = 2 << 3
ToolLevelReupload = 2 << 4
ToolSongAdd = 2 << 5
ModRateLevel = 2 << 6
ModRateDemon = 2 << 7
ModRegularBadge = 2 << 8
ModElderBadge = 2 << 9
ClaimDailyChest = 2 << 10
CommandSetAcc = 2 << 11
CommandRename = 2 << 12
ModReqMod = 2 << 13
ModSuggestLevel = 2 << 14
ModBanUser = 2 << 15
ModSetDaily = 2 << 16

__version__ = "InDev"
