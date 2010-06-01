#!/usr/bin/env python

""" Lector: textwidget.py

    Copyright (C) 2008 Davide Setti

    This program is released under the GNU GPLv2
"""

from __future__ import with_statement
from PyQt4 import QtGui


class TextWidget(QtGui.QTextBrowser):
    def __init__(self, parent = None):
        QtGui.QTextBrowser.__init__(self)

        self.setReadOnly(False)


    def saveAs(self, filename):
        from os import popen
        from shutil import move

        ## TODO: replace with Qt's temp files
        fileTmp = '/tmp/prova.html'
        s = self.document().toHtml('utf-8').toUtf8()
        with open(fileTmp, 'w') as fd:
            fd.write(s)

        cmd = "abiword --to=rtf %s" % (fileTmp, )
        popen(cmd)

        fileTmpRtf = fileTmp.split('.')[0] + '.rtf'
        move(fileTmpRtf, filename)

