[![Documentation Status](https://readthedocs.org/projects/gdpys/badge/?version=latest)](https://gdpys.readthedocs.io/en/latest/?badge=latest) [![Actions Status](https://github.com/RealistikDash/GDPyS/workflows/build/badge.svg)](https://github.com/RealistikDash/GDPyS/actions) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
# GDPyS (Rewrite)

GDPyS is a modern Geometry Dash Custom Server which can be utilised in the creation of Private Servers. It is written using Python, amking it fast and capable.

## Why GDPyS?

When designing GDPyS, we have decided on a set of key principles to follow. Firstly, it has to be simple to set up. This has been achieved by having a simple setup procedure only requiring the users to set up MySQL and Python. The next principle was the commitment to keep things as fast as possible. This was achieved through the use of caching. Thanks to the object oriented design, we were able to limit the amount of SQL queries required, increasing the speed and relieving load off the database (especially during surge scenarios).

Furthermore, GDPyS provides a unique range of features, ranging from plugins to custom magic sections. This makes GDPyS perfect for any type of GDPS, no matter the size

## The technical stuff...

### Requirements

Due to GDPyS' major advances within the GDPS space, its requirements are completely different to previous alternatives. Here are the requirements to run a GDPyS server:
- Device/Server capable of running Python (Linux VPS is recommended)
- Python 3.7+
- MySQL Server
- Domain name ~17 characters long (can be a bit more or less if using a few exe tweaks or if using hosts file)
