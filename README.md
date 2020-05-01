# GDPyS
GDPyS is a Python based Geometry Dash server, which can be used for making Privarte Servers.

# What works?
GDPyS is still in **very** early development. This means that most things aren't completed and some things may not work as intended. So here is what is currently done:
- Registering
- Logging in (no password check yet)
- Loading user data
- Updating user data
- Loading account comments
- Creating account comments
- Updating account settings
- Leaderboards (only top and creators)
- Saving user data
- Loading user data

# Why GDPyS?
GDPyS is made with convenience and performance in mind. It provides performance benefits over existing alternatives while convenient features (such as error logs for easier debugging and automatic cron). Additionally, it is designed to be directly swappable with Cvolton's GMDPrivateServer, meaning you will able to reuse your existing database, save and level files.

# Requirements
The requirements for GDPyS are different to existing alternatives. They include:
- A Linux VPS (required to run Python apps, any free hosting won't do)
- Python 3.5+ (tested with 3.6.9 and 3.7.5)
- Nginx/Apache (required to proxypass)
- 17 character domain (eg devvgdpys.ussr.pl)

# License
GDPyS is licensed under the [GNU General Public License v3.0](https://github.com/RealistikDash/GDPyS/blob/master/LICENSE)
