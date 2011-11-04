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
from PyQt4.Qt import QSize, QAction
from PyQt4.QtGui import QFont, QFileDialog, QPrinter, QMouseEvent, QTextCursor
from PyQt4.QtGui import QTextCharFormat, QTextOption
from PyQt4.QtCore import pyqtSignal, QEvent

from spellchecker import Highlighter, SpellAction

# workaroung to run textwidget outside of Lector
cmd_folder = os.path.dirname(os.path.abspath(__file__))
cmd_folder += "/../"
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import ui.resources_rc
from utils import settings
from settingsdialog import Settings

class EditorBar(QToolBar):
    saveDocAsSignal = pyqtSignal()
    spellSignal = pyqtSignal(bool)
    whiteSpaceSignal = pyqtSignal(bool)    
    boldSignal = pyqtSignal(bool)
    italicSignal = pyqtSignal(bool)
    underlineSignal = pyqtSignal(bool)
    strikethroughSignal = pyqtSignal(bool)
    subscriptSignal = pyqtSignal(bool)
    superscriptSignal = pyqtSignal(bool)

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
        
        self.spellAction = QAction('Spellchecking', self)
        self.spellAction.setIcon(QtGui.QIcon(":/icons/icons/tools-check-spelling.png"))
        self.spellAction.setCheckable(True)
        self.spellAction.setChecked(settings.get('editor:spell'))
        self.spellAction.toggled.connect(self.spell)
        self.insertSeparator(self.spellAction)
        self.addAction(self.spellAction)
        
        self.whiteSpaceAction = QAction('Show whitespace', self)
        self.whiteSpaceAction.setIcon(QtGui.QIcon(":/icons/icons/whiteSpace.png"))
        self.whiteSpaceAction.setCheckable(True)
        self.whiteSpaceAction.setChecked(settings.get('editor:whiteSpace'))
        self.whiteSpaceAction.toggled.connect(self.whiteSpace)
        self.addAction(self.whiteSpaceAction)
        
        self.BoldAction = QtGui.QAction(
                QtGui.QIcon(":/icons/icons/format-text-bold.png"),
                "&Bold", self, priority=QtGui.QAction.LowPriority,
                shortcut=QtCore.Qt.CTRL + QtCore.Qt.Key_B,
                triggered=self.bold, checkable=True)
        self.addAction(self.BoldAction)
        
        self.ItalicAction = QAction('Italic', self)
        self.ItalicAction.setIcon(QtGui.QIcon(":/icons/icons/format-text-italic.png"))
        self.ItalicAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_I)        
        self.ItalicAction.setCheckable(True)
        self.ItalicAction.triggered.connect(self.italic)
        self.addAction(self.ItalicAction)
         
        self.UnderlineAction = QAction('Underline', self)
        self.UnderlineAction.setIcon(QtGui.QIcon(":/icons/icons/format-text-underline.png"))
        self.UnderlineAction.setCheckable(True)
        self.UnderlineAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_U)
        self.UnderlineAction.triggered.connect(self.underline)
        self.addAction(self.UnderlineAction)
        
        self.StrikethroughAction = QAction('Strikethrough', self)
        self.StrikethroughAction.setIcon(QtGui.QIcon(":/icons/icons/format-text-strikethrough.png"))
        self.StrikethroughAction.setCheckable(True)
        self.StrikethroughAction.triggered.connect(self.strikethrough)
        self.addAction(self.StrikethroughAction)

        self.SubscriptAction = QAction('Subscript', self)
        self.SubscriptAction.setIcon(QtGui.QIcon(":/icons/icons/format-text-subscript.png"))
        self.SubscriptAction.setCheckable(True)
        self.SubscriptAction.triggered.connect(self.subscript)
        self.addAction(self.SubscriptAction)
        
        self.SuperscriptAction = QAction('Superscript', self)
        self.SuperscriptAction.setIcon(QtGui.QIcon(":/icons/icons/format-text-superscript.png"))
        self.SuperscriptAction.setCheckable(True)
        self.SuperscriptAction.triggered.connect(self.superscript)
        self.addAction(self.SuperscriptAction)

    def settings(self):
        lectorSettings = Settings(self, 1)
#        QObject.connect(lectorSettings, SIGNAL('accepted()'),
#                    self.updateTextEditor)
        lectorSettings.show()

    def SaveDocumentAs(self):
        self.saveDocAsSignal.emit()

    def spell(self):
        state = self.spellAction.isChecked()
        self.spellSignal.emit(state)
        
    def whiteSpace(self):
        state = self.whiteSpaceAction.isChecked()
        self.whiteSpaceSignal.emit(state)
        
    def toggleFormat(self, CharFormat):
        font = CharFormat.font()
        self.BoldAction.setChecked(font.bold())
        self.ItalicAction.setChecked(font.italic())
        self.UnderlineAction.setChecked(font.underline())
        self.StrikethroughAction.setChecked(CharFormat.fontStrikeOut())
        if CharFormat.verticalAlignment() == QtGui.QTextCharFormat.AlignSuperScript:
            self.SubscriptAction.setChecked(False)
            self.SuperscriptAction.setChecked(True)
        elif CharFormat.verticalAlignment() == QtGui.QTextCharFormat.AlignSubScript:
            self.SubscriptAction.setChecked(True)
            self.SuperscriptAction.setChecked(False)
        else:
            self.SubscriptAction.setChecked(False)
            self.SuperscriptAction.setChecked(False)
            
    def bold(self):
        state = self.BoldAction.isChecked()
        self.boldSignal.emit(state)

    def italic(self):
        state = self.ItalicAction.isChecked()
        self.italicSignal.emit(state)

    def underline(self):
        state = self.UnderlineAction.isChecked()
        self.underlineSignal.emit(state)

    def strikethrough(self):
        state = self.StrikethroughAction.isChecked()
        self.strikethroughSignal.emit(state)

    def subscript(self):
        state = self.SubscriptAction.isChecked()
        self.subscriptSignal.emit(state)

    def superscript(self):
        state = self.SuperscriptAction.isChecked()
        self.superscriptSignal.emit(state)


class TextWidget(QtGui.QTextEdit):
    fontFormatSignal = pyqtSignal(QtGui.QTextCharFormat)
    
    def __init__(self, parent = None):
        QtGui.QTextEdit.__init__(self)

        self.setupEditor()
        state = settings.get('editor:spell')
        if state == "":  # no settings
            state = True
        self.toggleSpell(state)
        
        on = settings.get('editor:whiteSpace')
        if on == "":  # no settings
            on = True
        self.togglewhiteSpace(on)

        self.currentCharFormatChanged.connect(
                self.CharFormatChanged)       
       
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

    def stopSpellchecker(self):
        if hasattr (self, 'highlighter'):
            self.highlighter.setDocument(None)
            self.dict = None

    def toggleSpell(self, state):
        if state:
            self.initSpellchecker()
        else:
            self.stopSpellchecker()
        settings.set('editor:spell', state)
        
    def togglewhiteSpace(self, on=True):
        """
        Show or hide whitespace and line ending markers
        """
        option = QTextOption()
        if on:
            option.setFlags(QTextOption.ShowTabsAndSpaces | QTextOption.ShowLineAndParagraphSeparators)
        else:
            option.setFlags(option.flags() & ~option.ShowTabsAndSpaces & ~option.ShowLineAndParagraphSeparators)
        self.document().setDefaultTextOption(option)
        settings.set('editor:whiteSpace', on)
        
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
            if event.key() == Qt.Key_Q:
                self.stopSpellchecker()
                handled = True
            if event.key() == Qt.Key_E:
                self.initSpellchecker()
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
            newText = newText.replace(u"\u2029", ' ')  # unicode "\n"

        cursor.insertText(newText)
        cursor.endEditBlock()

    def CharFormatChanged(self, CharFormat):
        self.fontFormatSignal.emit(CharFormat)
        
    def toggleBold(self, isChecked):
        self.setFontWeight(isChecked and QFont.Normal
                if self.fontWeight() > QFont.Normal else QFont.Bold)

    def toggleItalic(self, isChecked):
        self.setFontItalic(isChecked and not self.fontItalic())

    def toggleUnderline(self, isChecked):
        self.setFontUnderline(isChecked and not self.fontUnderline())

    def toggleStrikethrough(self, isChecked):
        format = self.currentCharFormat() 
        format.setFontStrikeOut(isChecked and not format.fontStrikeOut())
        self.mergeCurrentCharFormat(format) 

    def toggleSubscript(self, isChecked):
        format = self.currentCharFormat() 
        format.setVerticalAlignment(isChecked and
                        QTextCharFormat.AlignSubScript)
        self.mergeCurrentCharFormat(format)

    def toggleSuperscript(self, isChecked):
        format = self.currentCharFormat() 
        format.setVerticalAlignment(isChecked and 
                        QTextCharFormat.AlignSuperScript)
        self.mergeCurrentCharFormat(format)


    def saveAs(self):
        if settings.get("file_dialog_dir"):
            self.curDir = '~/'
        else:
            self.curDir = settings.get("file_dialog_dir")
            
        filename = unicode(QFileDialog.getSaveFileName(self,
                self.tr("Save document"), self.curDir,
                self.tr("ODT document (*.odt);;Text file (*.txt);;HTML file (*.html);;PDF file(*.pdf)")
                ))
        if not filename: return

        self.curDir = os.path.dirname(filename)
        settings.set("file_dialog_dir", self.curDir)
        
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
        self.showWhiteSpace(False)
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
    textEditorBar.spellSignal.connect(textEditor.toggleSpell)
    textEditorBar.whiteSpaceSignal.connect(textEditor.togglewhiteSpace)    
    textEditorBar.boldSignal.connect(textEditor.toggleBold)
    textEditorBar.italicSignal.connect(textEditor.toggleItalic)
    textEditorBar.underlineSignal.connect(textEditor.toggleUnderline)
    textEditorBar.strikethroughSignal.connect(textEditor.toggleStrikethrough)
    textEditorBar.subscriptSignal.connect(textEditor.toggleSubscript)
    textEditorBar.superscriptSignal.connect(textEditor.toggleSuperscript)
    
    textEditor.fontFormatSignal.connect(textEditorBar.toggleFormat)
    
    mwTextEditor.addToolBar(textEditorBar) 
    mwTextEditor.setCentralWidget(textEditor)

    mwTextEditor.show()

    return app.exec_()
    
if __name__ == '__main__':
    sys.exit(main())
