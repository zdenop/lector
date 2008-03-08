#!/usr/bin/env python

""" Lector: textwidget.py

    Copyright (C) 2008 Davide Setti

    This program is released under the GNU GPLv2
"""

from PyQt4 import QtCore, QtGui


class TextWidget(QtGui.QTextBrowser):
    def __init__(self, parent = None):
        QtGui.QTextBrowser.__init__(self)

        self.setReadOnly(False)


    def saveAs(self, filename):
        print filename
