# Posttid

Posttid is a program that takes the user's requests and constantly queries from the online bulletin board system, Reddit. With Posttid, individuals can be notified when posts on Reddit are created with their desired topic.

## How to run

Posttid was designed to run on Linux systems. Although running Posdit on Mac OSX can be possible, it has not been tested.

[Praw](https://praw.readthedocs.io/en/stable/), [Pyqt5](https://www.riverbankcomputing.com/software/pyqt/download5), and [Python-2.7.x](https://www.python.org/downloads/) are required for Posdit to run correctly.

    apt-get install python-pyqt5
    pip install praw
    git clone https://github.com/kevin-lam/Posttid.git
    cd Posttid
    ./main.py

## How to use

- Press the settings button to enter the settings window.
- Enter an email to receive notifications of posts matching your requests.
- Right click on the table to start adding, removing, or editing requests.
- Press the done button to save your requests and start the querying process.
- Check the disable checkbox to temporarily stop the querying. Uncheck to restart it.

## Licensing

Copyright (C) 2016  Kevin Lam

Posttid is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
