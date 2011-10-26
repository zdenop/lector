#!/usr/bin/env python

""" Lector: textwidget.py

    Copyright (C) 2011 Davide Setti

    This program is released under the GNU GPLv2
"""

from __future__ import with_statement
from PyQt4 import QtGui
from utils import settings

class TextWidget(QtGui.QTextEdit):
    def __init__(self, parent = None):
        QtGui.QTextEdit.__init__(self)

        self.setReadOnly(False)
        self.setupEditor()

    def setupEditor(self):
        '''
        Init editor settings
        '''
        self.setFont(QtGui.QFont(settings.get('editor:font')))


    def saveAs(self, filename):
        dw = QtGui.QTextDocumentWriter()
        dw.setFormat('ODF')  # Default format

        # Check for alternative output format
        if filename.rsplit('.', 1)[1] == "txt":
            dw.setFormat('plaintext')
        if filename.rsplit('.', 1)[1] in ("html", "htm"):
            dw.setFormat('HTML')

        dw.setFileName(filename)
        dw.write(self.document())

