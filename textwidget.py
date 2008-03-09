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
        from os import popen
        from shutil import move

        fileTmp = '/tmp/prova.html'
        s = self.document().toHtml('utf-8').toUtf8()
        fd = open(fileTmp, 'w')
        fd.write(s)
        fd.close()

        cmd = "abiword --to=rtf %s" % (fileTmp, )
        popen(cmd)

        fileTmpRtf = fileTmp.split('.')[0] + '.rtf'
        print fileTmpRtf
        move(fileTmpRtf, filename)
