#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Lector: textwidget.py

    Copyright (C) 2011 Davide Setti

    This program is released under the GNU GPLv2
"""

from __future__ import with_statement
import re

from PyQt4 import QtGui,QtCore
from PyQt4.Qt import Qt, QMenu
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
        contextMenu.addSeparator()
        contextMenu.addAction(clearAction)
        if not len(self.toPlainText()):
            clearAction.setEnabled(False)
        QtCore.QObject.connect(clearAction, QtCore.SIGNAL("triggered()"), self.clear)

        textOpsMenu = QMenu('Text change...')
        if not self.textCursor().hasSelection():
            textOpsMenu.setEnabled(False)

        removeEOLAction = QtGui.QAction("Join lines", textOpsMenu, )
        textOpsMenu.addAction(removeEOLAction)
        if not len(self.toPlainText()):
            clearAction.setEnabled(False)
        QtCore.QObject.connect(removeEOLAction, QtCore.SIGNAL("triggered()"), self.removeEOL)

        textOpsMenu.addSeparator()

        toUppercaseAction = QtGui.QAction("to UPPERCASE", textOpsMenu)
        textOpsMenu.addAction(toUppercaseAction)
        QtCore.QObject.connect(toUppercaseAction, QtCore.SIGNAL("triggered()"), self.toUppercase)

        toLowercaseAction = QtGui.QAction("to lowercase", textOpsMenu)
        textOpsMenu.addAction(toLowercaseAction)
        QtCore.QObject.connect(toLowercaseAction, QtCore.SIGNAL("triggered()"), self.toLowercase)

        toTitleAction = QtGui.QAction("to Title", textOpsMenu)
        textOpsMenu.addAction(toTitleAction)
        QtCore.QObject.connect(toTitleAction, QtCore.SIGNAL("triggered()"), self.toTitlecase)

        toCapsAction = QtGui.QAction("to Capitalize", textOpsMenu, )
        textOpsMenu.addAction(toCapsAction)
        QtCore.QObject.connect(toCapsAction, QtCore.SIGNAL("triggered()"), self.toCaps)

        contextMenu.insertSeparator(contextMenu.actions()[0])
        contextMenu.insertMenu(contextMenu.actions()[0], textOpsMenu)

        contextMenu.exec_(event.globalPos())
        event.accept()

    def toUppercase(self):
        self.changeText(self.getSelectedText(), 1)

    def toLowercase(self):
        self.changeText(self.getSelectedText(), 2)

    def toTitlecase(self):
        self.changeText(self.getSelectedText(), 3)

    def toCaps(self):
        self.changeText(self.getSelectedText(), 4)

    def removeEOL(self):
        self.changeText(self.getSelectedText(), 5)

    def getSelectedText(self):
        return unicode(self.textCursor().selectedText())

    def changeText(self, newText, conversion = 0):
        '''
        Replaces the selected text with newText.
        conversion = 0 => no conversion
        conversion = 1 => UPPERCASE
        conversion = 2 => lowercase
        conversion = 3 => Title (First Letter In Word)
        conversion = 4 => Capitalize First letter of sentence
        conversion = 5 => Remove end of lines
        '''
        ## TODO(zdposter): conversion = 6 => Remove multiple space ;-)
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.removeSelectedText()

        if conversion == 1:
            newText = newText.upper()
        if conversion == 2:
            newText = newText.lower()
        if conversion == 3:
            newText = newText.title()
        if conversion == 4:
            # newText = newText.capitalize()
            # This will capitalize Letters after ".", "?","!"
            rtn = re.split('([.!?] *)', newText)
            newText = ''.join([each.capitalize() for each in rtn])
            #TODO(zdposter): '."' '.\n' ignore after '"' ')'
        if conversion == 5:
            tempText = QtCore.QString()
            newText = newText.replace(u"\u2029", ' ')  # unicode "\n"

        cursor.insertText(newText)
        cursor.endEditBlock()

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
            else:
                return QtGui.QTextEdit.keyPressEvent(self, event)
            if handled:
                event.accept()
                return
        else:
            QtGui.QTextEdit.keyPressEvent(self, event)