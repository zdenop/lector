#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Lector: textwidget.py

    Copyright (C) 2011-2014 Davide Setti, Zdenko Podobný

    This program is released under the GNU GPLv2
"""
#pylint: disable-msg=C0103

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

# workaroung to run textwidget outside of Lector
CMD_FOLDER = os.path.dirname(os.path.abspath(__file__))
CMD_FOLDER += "/../../"
if CMD_FOLDER not in sys.path:
    sys.path.insert(0, CMD_FOLDER)

from lector.ui import resources_rc
from lector.utils import settings
from lector.settingsdialog import Settings
from lector.editor.spellchecker import Highlighter, SpellAction

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
        self.setIconSize(QSize(16, 16))
        self.createActions()

    def createActions(self):
        self.settingsAction = QAction(self.tr("Settings"), self)
        self.settingsAction.setIcon(QtGui.QIcon(":/icons/icons/configure.png"))
        self.settingsAction.triggered.connect(self.settings)
        self.addAction(self.settingsAction)

        self.saveDocAsAction = QAction(self.tr("Save As"), self)
        self.saveDocAsAction.triggered.connect(self.SaveDocumentAs)
        self.saveDocAsAction.setIcon(QtGui.QIcon(":/icons/icons/filesave.png"))
        self.addAction(self.saveDocAsAction)

        self.spellAction = QAction(self.tr("Spellchecking"), self)
        self.spellAction.setIcon(
            QtGui.QIcon(":/icons/icons/tools-check-spelling.png"))
        self.spellAction.setCheckable(True)
        self.spellAction.setChecked(settings.get('editor:spell'))
        self.spellAction.toggled.connect(self.spell)
        self.insertSeparator(self.spellAction)
        self.addAction(self.spellAction)

        self.whiteSpaceAction = QAction(self.tr("Show whitespace"), self)
        self.whiteSpaceAction.setIcon(
            QtGui.QIcon(":/icons/icons/whiteSpace.png"))
        self.whiteSpaceAction.setCheckable(True)
        self.whiteSpaceAction.setChecked(settings.get('editor:whiteSpace'))
        self.whiteSpaceAction.toggled.connect(self.whiteSpace)
        self.addAction(self.whiteSpaceAction)

        self.BoldAction = QtGui.QAction(
                QtGui.QIcon(":/icons/icons/format-text-bold.png"),
                self.tr("&Bold"), self,
                shortcut=QtCore.Qt.CTRL + QtCore.Qt.Key_B,
                triggered=self.bold, checkable=True)
        self.addAction(self.BoldAction)

        self.ItalicAction = QAction(self.tr("Italic"), self)
        self.ItalicAction.setIcon(
            QtGui.QIcon(":/icons/icons/format-text-italic.png"))
        self.ItalicAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_I)
        self.ItalicAction.setCheckable(True)
        self.ItalicAction.triggered.connect(self.italic)
        self.addAction(self.ItalicAction)

        self.UnderlineAction = QAction(self.tr("Underline"), self)
        self.UnderlineAction.setIcon(
            QtGui.QIcon(":/icons/icons/format-text-underline.png"))
        self.UnderlineAction.setCheckable(True)
        self.UnderlineAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_U)
        self.UnderlineAction.triggered.connect(self.underline)
        self.addAction(self.UnderlineAction)

        self.StrikethroughAction = QAction(self.tr("Strikethrough"), self)
        self.StrikethroughAction.setIcon(
            QtGui.QIcon(":/icons/icons/format-text-strikethrough.png"))
        self.StrikethroughAction.setCheckable(True)
        self.StrikethroughAction.triggered.connect(self.strikethrough)
        self.addAction(self.StrikethroughAction)

        self.SubscriptAction = QAction(self.tr("Subscript"), self)
        self.SubscriptAction.setIcon(
            QtGui.QIcon(":/icons/icons/format-text-subscript.png"))
        self.SubscriptAction.setCheckable(True)
        self.SubscriptAction.triggered.connect(self.subscript)
        self.addAction(self.SubscriptAction)

        self.SuperscriptAction = QAction(self.tr("Superscript"), self)
        self.SuperscriptAction.setIcon(
            QtGui.QIcon(":/icons/icons/format-text-superscript.png"))
        self.SuperscriptAction.setCheckable(True)
        self.SuperscriptAction.triggered.connect(self.superscript)
        self.addAction(self.SuperscriptAction)

    def settings(self):
        lectorSettings = Settings(self, 1)
#        QObject.connect(lectorSettings, SIGNAL('accepted()'),
#                    self.updateTextEditor)
        lectorSettings.settingAccepted.connect(self.resetSpell)
        lectorSettings.show()

    def SaveDocumentAs(self):
        self.saveDocAsSignal.emit()

    def spell(self):
        state = self.spellAction.isChecked()
        self.spellSignal.emit(state)

    def resetSpell(self):
        '''
        Turn off and on spellcheckig to use correct dictionary
        '''
        state = self.spellAction.isChecked()
        if state:
            self.spellSignal.emit(False)
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
        if CharFormat.verticalAlignment() == \
                QtGui.QTextCharFormat.AlignSuperScript:
            self.SubscriptAction.setChecked(False)
            self.SuperscriptAction.setChecked(True)
        elif CharFormat.verticalAlignment() == \
                QtGui.QTextCharFormat.AlignSubScript:
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
    spell = False
    symbols = [u"…", u"–", u"—"]  # ellipsis, n-dash, m-dash

    def __init__(self, parent = None):
        QtGui.QTextEdit.__init__(self)

        self.setupEditor()
        state = settings.get('editor:spell')
        if state == "":  # no settings
            state = True
        self.toggleSpell(state)

        onOff = settings.get('editor:whiteSpace')
        if onOff == "":  # no settings
            onOff = True
        self.togglewhiteSpace(onOff)

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
        # TODO: disable spellchecker icon in case of not working enchant
        try:
            import enchant
            spellDictDir = settings.get('spellchecker:directory')
            if spellDictDir:
                if enchant.__ver_major__ >= 1 and enchant.__ver_minor__ >= 6:
                    enchant.set_param("enchant.myspell.dictionary.path",
                                      spellDictDir)
                else:
                    print "Your pyenchant version is to old. Please " \
                          "upgrade to version 1.6.0 or higher, if you want " \
                          "to use spellchecker."
                    return None

            spellLang = settings.get('spellchecker:lang')
            if enchant.dict_exists(spellLang):
                self.dict = enchant.Dict(spellLang)
            else:
                # try dictionary based on the current locale
                try:
                    self.dict = enchant.Dict()
                    settings.set('spellchecker:lang', self.dict.tag)
                except:  # we don not have working dictionary...
                    return None
            if self.dict:
                self.usePWL(self.dict)

        except:
            print "can not start spellchecker!!!"
            import traceback
            traceback.print_exc()
            return None

    def stopSpellchecker(self):
        if hasattr (self, 'highlighter'):
            self.highlighter.setDocument(None)
            self.dict = None
            self.spell = False

    def toggleSpell(self, state):
        if state:
            self.initSpellchecker()
        else:
            self.stopSpellchecker()
        settings.set('editor:spell', state)


    def togglewhiteSpace(self, state=True):
        """
        Show or hide whitespace and line ending markers
        """
        option = QTextOption()
        if state:
            option.setFlags(QTextOption.ShowTabsAndSpaces |
                            QTextOption.ShowLineAndParagraphSeparators)
        else:
            option.setFlags(option.flags() & ~option.ShowTabsAndSpaces &
                            ~option.ShowLineAndParagraphSeparators)
        self.document().setDefaultTextOption(option)
        settings.set('editor:whiteSpace', state)

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
            elif event.key() == Qt.Key_E:
                self.initSpellchecker()
                handled = True
            elif event.key() == Qt.Key_F1:
                self.toCaps()
                handled = True
            elif event.key() == Qt.Key_F2:
                self.removeEOL()
                handled = True
            elif event.key() == Qt.Key_O and event.modifiers() & \
                    Qt.AltModifier:
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
        """ Creates two context menus:
            1. no modifier -> spellchecker & clear emnu
            2. ctrl modifier -> Text change & Insert symbol
        """
        contextMenu = self.createStandardContextMenu()
        spellMenu = True

        if (QApplication.keyboardModifiers() & Qt.ControlModifier):
            spellMenu = False

        self.clearAction = QtGui.QAction(self.tr("Clear"), contextMenu)
        contextMenu.addSeparator()
        contextMenu.addAction(self.clearAction)
        if not len(self.toPlainText()):
            self.clearAction.setEnabled(False)
        QtCore.QObject.connect(self.clearAction,
                               QtCore.SIGNAL("triggered()"), self.clear)
        if not spellMenu:
            textOpsMenu = QMenu(self.tr("Text change..."))

            removeEOLAction = QtGui.QAction(self.tr("Join lines"),
                                            textOpsMenu, )
            textOpsMenu.addAction(removeEOLAction)
            QtCore.QObject.connect(removeEOLAction,
                                   QtCore.SIGNAL("triggered()"),
                                   self.removeEOL)

            textOpsMenu.addSeparator()

            toUppercaseAction = QtGui.QAction(self.tr("to UPPERCASE"),
                                              textOpsMenu)
            textOpsMenu.addAction(toUppercaseAction)
            QtCore.QObject.connect(toUppercaseAction,
                                   QtCore.SIGNAL("triggered()"),
                                   self.toUppercase)

            toLowercaseAction = QtGui.QAction(self.tr("to lowercase"),
                                              textOpsMenu)
            textOpsMenu.addAction(toLowercaseAction)
            QtCore.QObject.connect(toLowercaseAction,
                                   QtCore.SIGNAL("triggered()"),
                                   self.toLowercase)

            toTitleAction = QtGui.QAction(self.tr("to Title"), textOpsMenu)
            textOpsMenu.addAction(toTitleAction)
            QtCore.QObject.connect(toTitleAction,
                                   QtCore.SIGNAL("triggered()"),
                                   self.toTitlecase)

            toCapsAction = QtGui.QAction(self.tr("to Capitalize"), textOpsMenu)
            textOpsMenu.addAction(toCapsAction)
            QtCore.QObject.connect(toCapsAction,
                                   QtCore.SIGNAL("triggered()"), self.toCaps)

            contextMenu.insertSeparator(contextMenu.actions()[0])
            contextMenu.insertMenu(contextMenu.actions()[0], textOpsMenu)

            insertSymbolMenu = QMenu(self.tr("Insert symbol..."))
            settings_symbols = settings.get('editor:symbols')
            if settings_symbols:
                self.symbols = settings_symbols.split('\n')
            for symbol in self.symbols:
                action = SpellAction(symbol, insertSymbolMenu)
                action.correct.connect( self.insertSymbol)
                insertSymbolMenu.addAction(action)

            contextMenu.insertMenu(contextMenu.actions()[0], insertSymbolMenu)

        if not self.textCursor().hasSelection() and spellMenu:
            # Select the word under the cursor for spellchecker
            cursor = self.textCursor()
            cursor.select(QTextCursor.WordUnderCursor)

            self.setTextCursor(cursor)
            text = unicode(self.textCursor().selectedText())

            #TODO: put to configuration list of ignored starting/ending chars
            # remove u"„" from selection
            if text.startswith(u"„") or text.startswith(u"“"):
                text = text[1:]
                selectionEnd = cursor.selectionEnd()
                cursor.setPosition(cursor.position() - len(text))
                cursor.setPosition(selectionEnd, QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
            # remove u"”" from selection
            if text.endswith(u"”") or text.startswith(u"“"):
                selectionEnd = cursor.selectionEnd()
                cursor.setPosition(cursor.position() - len(text))
                cursor.setPosition(selectionEnd - 1, QTextCursor.KeepAnchor)
                text = text[:-1]
                self.setTextCursor(cursor)

            # Check if the selected word is misspelled and offer spelling
            # suggestions if it is.
            if self.textCursor().hasSelection():
                if not self.dict.check(text):
                    spell_menu = QMenu(self.tr("Spelling Suggestions"))
                    addWordAcction = QAction(self.tr('Add word...'),
                                             spell_menu)
                    QtCore.QObject.connect(addWordAcction,
                               QtCore.SIGNAL("triggered()"), self.addWord)
                    #addWordAcction.triggered.connect(self.addWord)
                    spell_menu.addAction(addWordAcction)
                    for word in self.dict.suggest(text):
                        action = SpellAction(word, spell_menu)
                        action.correct.connect(self.changeText)
                        spell_menu.addAction(action)
                    contextMenu.insertSeparator(contextMenu.actions()[1])
                    contextMenu.insertMenu(contextMenu.actions()[0],
                                            spell_menu)
                    # Only add the spelling suggests to the menu if there are
                    # suggestions.
                    if len(spell_menu.actions()) != 1:
                        spell_menu.insertSeparator(spell_menu.actions()[1])


        contextMenu.exec_(event.globalPos())
        event.accept()

    def usePWL(self, dictionary):
        """ Restart spellchecker with personal private list
        """
        import enchant

        pwlDict = settings.get('spellchecker:pwlDict')
        pwlLang = settings.get('spellchecker:pwlLang')
        if pwlLang:
            try:
                (name, extension) = pwlDict.rsplit('.', 1)
                pwlDict = name + '_'  + dictionary.tag + "." + extension
            except:
                pwlDict = name + '_'  + dictionary.tag

        self.dict = enchant.DictWithPWL(dictionary.tag, pwlDict)
        self.highlighter = Highlighter(self.document())
        self.highlighter.setDict(self.dict)

    def addWord(self):
        """ Add word to personal private list
        """
        self.dict.add_to_pwl(self.getSelectedText())
        self.highlighter.rehighlight()

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
        pos1 = cursor.position()

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
            newText = re.sub(' +', ' ', newText)  # replace  multiple spaces

        cursor.insertText(newText)

        # Restore text selection
        pos2 = cursor.position()
        cursor.setPosition(pos1)
        cursor.setPosition(pos2, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

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
        charFmt = self.currentCharFormat()
        charFmt.setFontStrikeOut(isChecked and not charFmt.fontStrikeOut())
        self.mergeCurrentCharFormat(charFmt)

    def toggleSubscript(self, isChecked):
        charFmt = self.currentCharFormat()
        charFmt.setVerticalAlignment(isChecked and
                        QTextCharFormat.AlignSubScript)
        self.mergeCurrentCharFormat(charFmt)

    def toggleSuperscript(self, isChecked):
        charFmt = self.currentCharFormat()
        charFmt.setVerticalAlignment(isChecked and
                        QTextCharFormat.AlignSuperScript)
        self.mergeCurrentCharFormat(charFmt)


    def saveAs(self):
        if settings.get("file_dialog_dir"):
            self.curDir = '~/'
        else:
            self.curDir = settings.get("file_dialog_dir")

        filename = unicode(QFileDialog.getSaveFileName(self,
                self.tr("Save document"), self.curDir,
                self.tr("ODT document (*.odt);;Text file (*.txt);;"
                        "HTML file (*.html);;PDF file(*.pdf)")
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
                        self.tr("Error - Lector"),
                        self.tr("Can't open '%s.'" % fn))
                    else:
                        stream = QtCore.QTextStream(f)
                        text = unicode(stream.readAll())
                        self.setText(text)
                else:
                    QtGui.QMessageBox.information(self.parent(),
                    self.tr("Error - Lector"),
                    self.tr("'%s' is not a file." % fn))
        QtGui.QApplication.restoreOverrideCursor()

    def filePrintPdf(self, fn):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        printer.setOutputFileName(fn)
        printer.setOutputFormat(QPrinter.PdfFormat)
        self.document().print_(printer)

    def insertSymbol(self, symbol):
        """
        insert symbol
        """
        self.insertPlainText(symbol)

def main():
    """ Main loop to run text widget as applation
    """
    app = QApplication(sys.argv)

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
