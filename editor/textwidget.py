#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Lector: textwidget.py

    Copyright (C) 2011 Davide Setti

    This program is released under the GNU GPLv2
"""

from __future__ import with_statement
import os
import sys
import re

from PyQt4 import QtGui, QtCore
from PyQt4.Qt import Qt, QMenu, QApplication, QMainWindow, QToolBar
from PyQt4.Qt import QSize, QObject, SIGNAL, QString
from PyQt4.QtGui import QFont, QFileDialog, QPrinter, QPrintPreviewDialog

from spellchecker import *

# workaroung to run textwidget outside of Lector
cmd_folder = os.path.dirname(os.path.abspath(__file__))
cmd_folder += "/../"
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import ui.resources_rc
from utils import settings
from settingsdialog import Settings
from ui.ui_lector import Ui_Lector

class EditorBar(QToolBar):
    saveDocAsSignal = pyqtSignal()
    boldSignal = pyqtSignal()
    italicSignal = pyqtSignal()
    underlineSignal = pyqtSignal()
    strikethroughSignal = pyqtSignal()
    subscriptSignal = pyqtSignal()
    superscriptSignal = pyqtSignal()

    def __init__(self, parent = None):
        QtGui.QToolBar.__init__(self,  parent)
        self.setWindowTitle('EditorBar')
        self.setIconSize(QSize(16,16))
        self.createActions()

    def createActions(self):
        self.settingsAction = QAction('Settings', self)
        self.settingsAction.setIcon(QtGui.QIcon(":/icons/icons/configure.png"))
        self.settingsAction.triggered.connect(self.settings)
        self.addAction(self.settingsAction)
        
        self.saveDocAsAction = QAction('Save As', self)
        self.saveDocAsAction.triggered.connect(self.SaveDocumentAs)
        self.saveDocAsAction.setIcon(QtGui.QIcon(":/icons/icons/filesave.png"))
        self.addAction(self.saveDocAsAction)
        
        self.BoldAction = QAction('Bold', self)
        self.BoldAction.setIcon(QtGui.QIcon(":/icons/icons/format-text-bold.png"))
        self.BoldAction.triggered.connect(self.bold)
        self.insertSeparator(self.BoldAction)
        self.addAction(self.BoldAction)
        
        self.ItalicAction = QAction('Italic', self)
        self.ItalicAction.setIcon(QtGui.QIcon(":/icons/icons/format-text-italic.png"))
        self.ItalicAction.triggered.connect(self.italic)
        self.addAction(self.ItalicAction)
         
        self.UnderlineAction = QAction('Underline', self)
        self.UnderlineAction.setIcon(QtGui.QIcon(":/icons/icons/format-text-underline.png"))
        self.UnderlineAction.triggered.connect(self.underline)
        self.addAction(self.UnderlineAction)
        
        self.StrikethroughAction = QAction('Strikethrough', self)
        self.StrikethroughAction.setIcon(QtGui.QIcon(":/icons/icons/format-text-strikethrough.png"))
        self.StrikethroughAction.triggered.connect(self.strikethrough)
        self.addAction(self.StrikethroughAction)

        self.SubscriptAction = QAction('Subscript', self)
        self.SubscriptAction.setIcon(QtGui.QIcon(":/icons/icons/format-text-subscript.png"))
        self.SubscriptAction.triggered.connect(self.subscript)
        self.addAction(self.SubscriptAction)
        
        self.SuperscriptAction = QAction('Superscript', self)
        self.SuperscriptAction.setIcon(QtGui.QIcon(":/icons/icons/format-text-superscript.png"))
        self.SuperscriptAction.triggered.connect(self.superscript)
        self.addAction(self.SuperscriptAction)
        
    def bold(self):
        self.boldSignal.emit()

    def italic(self):
        self.italicSignal.emit()

    def underline(self):
        self.underlineSignal.emit()

    def strikethrough(self):
        self.strikethroughSignal.emit()

    def subscript(self):
        self.subscriptSignal.emit()

    def superscript(self):
        self.superscriptSignal.emit()

    def settings(self):
        settings = Settings(self, 1)
#        QObject.connect(settings, SIGNAL('accepted()'),
#                    self.updateTextEditor)
        settings.show()

    def SaveDocumentAs(self):
        self.saveDocAsSignal.emit()

class TextWidget(QtGui.QTextEdit):

    def __init__(self, parent = None):
        QtGui.QTextEdit.__init__(self)

        self.setupEditor()
        self.initSpellchecker()

    def setupEditor(self):
        '''
        Init editor settings
        '''
        self.setMouseTracking(True)
        self.setReadOnly(False)
        self.setEditorFont()

    def initSpellchecker(self):
        try: 
            import enchant
            spellDictDir = settings.get('spellchecker:directory')
            if spellDictDir:
                enchant.set_param("enchant.myspell.dictionary.path", spellDictDir)

            spellLang = settings.get('spellchecker:lang')
            if enchant.dict_exists(spellLang):
                self.dict = enchant.Dict(spellLang)
            else:
                # try dictionary based on the current locale
                self.dict = enchant.Dict()

            self.highlighter = Highlighter(self.document())
            self.highlighter.setDict(self.dict)
        except:
            print "can not start spellchecker!!!"
            import traceback
            traceback.print_exc()
            return None

    def mousePressEvent(self, event):
        """
        Select misspelled word after right click
        otherwise left clik + right click is needed.
        
        Originally from John Schember spellchecker
        """
        if event.button() == Qt.RightButton:
            # Rewrite the mouse event to a left button event so the cursor is
            # moved to the location of the pointer.
            event = QMouseEvent(QEvent.MouseButtonPress, event.pos(),
                Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        QtGui.QTextEdit.mousePressEvent(self, event)
        
    def setEditorFont(self):
        self.setFont(QtGui.QFont(settings.get('editor:font')))

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
            elif event.key() == Qt.Key_O and event.modifiers() & Qt.AltModifier:
                self.openFile()
                handled = True
            else:
                return QtGui.QTextEdit.keyPressEvent(self, event)
            if handled:
                event.accept()
                return
        else:
            QtGui.QTextEdit.keyPressEvent(self, event)

    def contextMenuEvent(self, event):
        contextMenu = self.createStandardContextMenu()
        
        self.clearAction = QtGui.QAction("Clear", contextMenu)
        contextMenu.addSeparator()
        contextMenu.addAction(self.clearAction)
        if not len(self.toPlainText()):
            self.clearAction.setEnabled(False)
        QtCore.QObject.connect(self.clearAction,
                               QtCore.SIGNAL("triggered()"), self.clear)

        textOpsMenu = QMenu('Text change...')

        removeEOLAction = QtGui.QAction("Join lines", textOpsMenu, )
        textOpsMenu.addAction(removeEOLAction)
        QtCore.QObject.connect(removeEOLAction,
                               QtCore.SIGNAL("triggered()"), self.removeEOL)

        textOpsMenu.addSeparator()

        toUppercaseAction = QtGui.QAction("to UPPERCASE", textOpsMenu)
        textOpsMenu.addAction(toUppercaseAction)
        QtCore.QObject.connect(toUppercaseAction,
                               QtCore.SIGNAL("triggered()"), self.toUppercase)

        toLowercaseAction = QtGui.QAction("to lowercase", textOpsMenu)
        textOpsMenu.addAction(toLowercaseAction)
        QtCore.QObject.connect(toLowercaseAction,
                               QtCore.SIGNAL("triggered()"), self.toLowercase)

        toTitleAction = QtGui.QAction("to Title", textOpsMenu)
        textOpsMenu.addAction(toTitleAction)
        QtCore.QObject.connect(toTitleAction,
                               QtCore.SIGNAL("triggered()"), self.toTitlecase)

        toCapsAction = QtGui.QAction("to Capitalize", textOpsMenu, )
        textOpsMenu.addAction(toCapsAction)
        QtCore.QObject.connect(toCapsAction,
                               QtCore.SIGNAL("triggered()"), self.toCaps)

        contextMenu.insertSeparator(contextMenu.actions()[0])
        contextMenu.insertMenu(contextMenu.actions()[0], textOpsMenu)

        if not self.textCursor().hasSelection():
            textOpsMenu.setEnabled(False)
            
            # Select the word under the cursor for spellchecker
            cursor = self.textCursor()
            cursor.select(QTextCursor.WordUnderCursor)
            self.setTextCursor(cursor)
            
            # Check if the selected word is misspelled and offer spelling
            # suggestions if it is.
            if self.textCursor().hasSelection():
                text = unicode(self.textCursor().selectedText())
                if not self.dict.check(text):
                    spell_menu = QMenu('Spelling Suggestions')
                    for word in self.dict.suggest(text):
                        action = SpellAction(word, spell_menu)
                        action.correct.connect(self.changeText)
                        spell_menu.addAction(action)
                    # Only add the spelling suggests to the menu if there are
                    # suggestions.
                    if len(spell_menu.actions()) != 0:
                        contextMenu.insertSeparator(contextMenu.actions()[0])
                        contextMenu.insertMenu(contextMenu.actions()[0], 
                                               spell_menu)

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


    def toggleBold(self):
        self.setFontWeight(QFont.Normal
                if self.fontWeight() > QFont.Normal else QFont.Bold)

    def toggleItalic(self):
        self.setFontItalic(not self.fontItalic())

    def toggleUnderline(self):
        self.setFontUnderline(not self.fontUnderline())

    def toggleStrikethrough(self):
        format = self.currentCharFormat() 
        format.setFontStrikeOut(not format.fontStrikeOut())
        self.mergeCurrentCharFormat(format) 

    def toggleSubscript(self):
        format = self.currentCharFormat() 
        format.setVerticalAlignment(
                        QTextCharFormat.AlignSubScript)
        self.mergeCurrentCharFormat(format)

    def toggleSuperscript(self):
        format = self.currentCharFormat() 
        format.setVerticalAlignment(
                        QTextCharFormat.AlignSuperScript)
        self.mergeCurrentCharFormat(format)


    def saveAs(self):
        #TODO: self.curDir
        filename = unicode(QFileDialog.getSaveFileName(self,
                #self.tr("Save document"), self.curDir,
                self.tr("Save document"), "",
                self.tr("ODT document (*.odt);;Text file (*.txt);;HTML file (*.html);;PDF file(*.pdf)")
                ))
        if not filename: return
        #self.curDir = os.path.dirname(fn)
        
        dw = QtGui.QTextDocumentWriter()
        dw.setFormat('ODF')  # Default format

        # Check for alternative output format
        if filename.rsplit('.', 1)[1] == "txt":
            dw.setFormat('plaintext')
        if filename.rsplit('.', 1)[1] in ("html", "htm"):
            dw.setFormat('HTML')
        if filename.rsplit('.', 1)[1] in ("PDF", "pdf"):
            self.filePrintPdf(filename)
            return
        dw.setFileName(filename)
        dw.write(self.document())

    def openFile(self):
        if settings.get("file_dialog_dir"):
            self.curDir = '~/'
        else:
            self.curDir = settings.get("file_dialog_dir")
        fn = unicode(QFileDialog.getOpenFileName(self,
                self.tr("Open File..."), self.curDir,
                self.tr("HTML-Files (*.htm *.html);;All Files (*)")))
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        if fn:
            self.lastFolder = os.path.dirname(fn)
            if os.path.exists(fn):
                if os.path.isfile(fn):
                    f = QtCore.QFile(fn)
                    if not f.open(QtCore.QIODevice.ReadOnly |
                                  QtCore.QIODevice.Text):
                        QtGui.QMessageBox.information(self.parent(),
                        "Error - Lector",
                        "Can't open %s."%fn)
                    else:
                        stream = QtCore.QTextStream(f)
                        text = unicode(stream.readAll())
                        self.setText(text)
                else:
                    QtGui.QMessageBox.information(self.parent(),
                    "Error - Lector",
                    "%s is not a file."%fn)
        QtGui.QApplication.restoreOverrideCursor()

    def filePrintPdf(self, fn):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setOutputFileName(fn)
        printer.setOutputFormat(QPrinter.PdfFormat)
        self.document().print_(printer)

def main(args=sys.argv):
    app = QApplication(args)


    mwTextEditor = QMainWindow() 
    textEditorBar = EditorBar(mwTextEditor)
    textEditor = TextWidget(textEditorBar)

    textEditorBar.saveDocAsSignal.connect(textEditor.saveAs)
    textEditorBar.boldSignal.connect(textEditor.toggleBold)
    textEditorBar.italicSignal.connect(textEditor.toggleItalic)
    textEditorBar.underlineSignal.connect(textEditor.toggleUnderline)
    textEditorBar.strikethroughSignal.connect(textEditor.toggleStrikethrough)
    textEditorBar.subscriptSignal.connect(textEditor.toggleSubscript)
    textEditorBar.superscriptSignal.connect(textEditor.toggleSuperscript)
    
    mwTextEditor.addToolBar(textEditorBar) 
    mwTextEditor.setCentralWidget(textEditor)

    mwTextEditor.show()

    return app.exec_()
    
if __name__ == '__main__':
    sys.exit(main())
