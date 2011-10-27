#!/usr/bin/env python

""" Lector: textwidget.py

    Copyright (C) 2011 Davide Setti

    This program is released under the GNU GPLv2
"""

from __future__ import with_statement
from PyQt4 import QtGui,QtCore
from PyQt4.Qt import Qt
from PyQt4.QtGui import QFont

from utils import settings

class TextWidget(QtGui.QTextEdit):
    def __init__(self, parent = None):
        QtGui.QTextEdit.__init__(self)

        self.setupEditor()

    def setupEditor(self):
        '''
        Init editor settings
        '''
        self.setMouseTracking(True)
        self.setReadOnly(False)
        self.setEditorFont()

    def setEditorFont(self):
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

    def contextMenuEvent(self, event):
        contextMenu = self.createStandardContextMenu()
        
        clearAction = QtGui.QAction("Clear", contextMenu)
        contextMenu.addAction(clearAction)
        if not len(self.toPlainText()):
            clearAction.setEnabled(False) 
        QtCore.QObject.connect(clearAction, QtCore.SIGNAL("triggered()"), self.clear)

        contextMenu.exec_(event.globalPos())
        event.accept()

    def toggleItalic(self):
        self.setFontItalic(not self.fontItalic())

    def toggleUnderline(self):
        self.setFontUnderline(not self.fontUnderline())
        
    def toggleBold(self):
        self.setFontWeight(QFont.Normal
                if self.fontWeight() > QFont.Normal else QFont.Bold)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            handled = False
            if event.key() == Qt.Key_B:
                self.toggleBold()
                handled = True
            elif event.key() == Qt.Key_I:
                self.toggleItalic()
                handled = True
            elif event.key() == Qt.Key_U:
                self.toggleUnderline()
                handled = True
            if handled:
                event.accept()
                return
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            #self.emit(SIGNAL("returnPressed()"))
            event.accept()
        else:
            QtGui.QTextEdit.keyPressEvent(self, event)