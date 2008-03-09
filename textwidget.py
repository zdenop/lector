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
        import os, codecs

        print filename
        fileTmp = '/tmp/prova.html'
#        s = unicode(self.toHtml().toUtf8(), 'utf8')

#        fd = codecs.open(fileTmp, 'w','utf-8')
        s = self.document().toHtml('utf-8').toUtf8()
        fd = open(fileTmp, 'w')
        fd.write(s)
        fd.close()

        cmd = "abiword --to=rtf %s" % (fileTmp, )
        os.popen(cmd)
