#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Functions to access settings
"""
#pylint: disable-msg=C0103

from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSettings, QVariant, QDir, QStandardPaths


def set(name, value):
    """ Set setting
    """
    settings = QSettings("Davide Setti", "Lector")
    settings.setValue(name, QVariant(value))

def get(name):
    """ Retrieve setting and convert result
    """
    home_dir = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
    stdPwlDict = home_dir + QDir.separator() + "my-dict.txt"
    settings = QSettings("Davide Setti", "Lector")
    if name == 'scanner:height':
        return int(settings.value(name, 297))
    elif name == 'scanner:width':
        return int(settings.value(name, 210))
    elif name == 'scanner:resolution':
        return int(settings.value(name, 300))
    elif name == 'scanner:mode':
        return str(settings.value(name, "Color"))
    elif name == 'scanner:device':
        return str(settings.value(name, ""))
    elif name == 'editor:font':
        return settings.value(name, QFont(QFont("Courier New", 10)))
    elif name == 'editor:symbols':
        return settings.value(name)
    elif name in ('editor:clear', 'editor:spell', 'editor:whiteSpace',
                  'spellchecker:pwlLang',):
        return str(settings.value(name, "true")).lower() == "true"
    elif name in ('log:errors'):
        return str(settings.value(name, "false")).lower() == "true"
    elif name == 'spellchecker:pwlDict':
        return str(settings.value(name, stdPwlDict))
    else:
        return str(settings.value(name, ""))


# for testing module funcionality
def main():
    """ Main loop to run test
    """
    home_dir = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
    print('home_dir:', home_dir)
    stdPwlDict = home_dir + QDir.separator() + "my-dict.txt"
    print('stdPwlDict:', stdPwlDict)

# MAIN
if __name__ == '__main__':
    import sys
    sys.exit(main())
