# GDPyS
GDPyS is a Python based Geometry Dash server, which can be used for making Private Servers.
Join the [discord server](https://discord.gg/Un42FEV) to follow the development of GDPyS.

## Major notes/changes
Here are a list of some changes server owners and operators may not be familiar with that are present in GDPyS.
- Bans are very harsh. Not only are people hidden from the leaderboards, they additionally can't login and (while its optional) have their levels hidden from search.
- Green users haave their abillities hugely cut down. For example, they can't upload levels, view leaderboards and more. While this may be bad in some cases, it overall makes your server more secure and makes it harder to bot.
- There is a custom Awarded and Magic section. Rather than being randomly selected by an arbitrary value, levels now have to be nominated by moderators.
- There is a completely new bitwise-based permission system. While it is more complex, it is faster and allows more to be done with it.
- Deleting levels doesn't fully delete them. Some of the metadata (that I deemed necessary in case of raids or exploits) is moved to a new table (called `deletedlevels`) and the level file is left untouched.

# Why GDPyS?
GDPyS is made with convenience and performance in mind. It provides performance benefits over existing alternatives while convenient features (such as error logs for easier debugging and automatic cron). Additionally, it is designed to be directly swappable with Cvolton's GMDPrivateServer, meaning you will able to reuse your existing database, save and level files.

# Cheatless

Cheatless is the GDPyS AntiCheat! It performs various tasks such as score analysis to keep obvious cheaters off your server. It is currently in heavy development but once finished, it will provide protection against cheaters. Each part of it can be enabled and disabled at will via the GDPyS config.

# Requirements
The requirements for GDPyS are different to existing alternatives. They include:
- Anything that can run Python such as a Linux VPS (required to run Python apps, any free hosting won't do)
- Python 3.7+ (tested on 3.7.5)
- Nginx/Apache (required to proxypass)
- MySQL Server
- Roughly 17 character domain such as devvgdpys.ussr.pl (more or less, few tweaks when editing the exe and routes could allow for more or less)

Read [the wiki](https://github.com/RealistikDash/GDPyS/wiki/How-to-set-up-GDPyS) for more information.

# Credits
- Some of this code is a direct port of [Cvolton's GMDPrivate Server](https://github.com/Cvolton/GMDprivateServer) into Python. Furthermore, his database structure has been used as a base.

# License
GDPyS is licensed under the [GNU General Public License v3.0](https://github.com/RealistikDash/GDPyS/blob/master/LICENSE)
