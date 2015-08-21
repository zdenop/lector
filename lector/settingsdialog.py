#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Lector utils

    Copyright (C) 2011-2014 Davide Setti, Zdenko Podobný
    Website: http://code.google.com/p/lector

    This program is released under the GNU GPLv2

"""
#pylint: disable-msg=C0103

import os
import sys

from PyQt4.QtGui import QDialog, QFontDialog, QFont, QFileDialog, \
    QMessageBox
from PyQt4.QtCore import pyqtSignature, pyqtSignal, QLocale, QDir, \
    QDirIterator

from ui.ui_settings import Ui_Settings
from utils import settings
from utils import get_spellchecker_languages

class Settings(QDialog):
    colors = ['Color', 'Gray', 'Lineart']
    settingAccepted = pyqtSignal()

    def __init__(self, parent = None, tabIndex = 0):
        QDialog.__init__(self, parent)

        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.ui.tabWidget.setCurrentIndex(tabIndex)
        self.initSettings()

    def changeFont(self, editorFont):
        self.ui.fontLabel.setFont(editorFont)
        label = editorFont.family().toAscii().data()
        label += ", %d pt" % editorFont.pointSize()
        self.ui.fontLabel.setText(label)

    def langList(self, spellDictDir):
        self.ui.dictBox.clear()
        langs = get_spellchecker_languages(spellDictDir)
        if langs == None:
            self.ui.spellInfoLabel.setText(self.tr(
                "Enchant not found. Check if pyenchant is installed!"))
        elif len(langs) == 0:
            self.ui.spellInfoLabel.setText(self.tr(
             "Enchant found but no dictionary. Check your dictionary directory."
             ))
        else:
            for lang in langs:
                self.ui.dictBox.addItem(lang)

            spellLang = settings.get('spellchecker:lang')
            currentIndex = self.ui.dictBox.findText(spellLang)
            if currentIndex > -1:
                self.ui.dictBox.setCurrentIndex(currentIndex)
            else:
                self.ui.spellInfoLabel.setText(self.tr("'%s' was not found in"
                    "available dictionaries. Using other dictionary." \
                    % spellLang ))

    def UItranslations(self):
        """ Get list of available ui translations
        """
        # iterate over resource file to find available translations
        fltr = QDir.Dirs | QDir.Files | QDir.Hidden
        iterator = QDirIterator(':', fltr, QDirIterator.Subdirectories)
        while iterator.hasNext():
            filePath = iterator.next()
            if '/translations/ts/' in filePath:
                fileName  = os.path.basename(unicode(filePath[1:]))
                locale = fileName.replace('lector_','').replace('.qm', '')
                if locale:
                    self.ui.cbLang.addItem(locale)
        locale = settings.get('ui:lang')
        if not locale:
            locale = QLocale.system().name()
        currentIndex = self.ui.cbLang.findText(locale)
        if currentIndex <= -1:
            currentIndex = self.ui.cbLang.findText('en_GB')
        self.ui.cbLang.setCurrentIndex(currentIndex)

    def initSettings(self):
        self.ui.sbHeight.setValue(settings.get('scanner:height'))
        self.ui.sbWidth.setValue(settings.get('scanner:width'))
        self.ui.sbResolution.setValue(settings.get('scanner:resolution'))
        self.ui.combColor.setCurrentIndex(
            self.colors.index(settings.get('scanner:mode')))

        self.changeFont(QFont(settings.get('editor:font')))
        self.ui.checkBoxClear.setChecked(settings.get('editor:clear'))
        settings_symbols = settings.get('editor:symbols')
        if settings_symbols:
            self.ui.symbolList.setPlainText(settings_symbols)

        spellDictDir = settings.get('spellchecker:directory')
        self.ui.directoryLine.setText(spellDictDir)
        self.langList(spellDictDir)
        self.UItranslations()
        self.ui.checkBoxPWL.setChecked(settings.get('spellchecker:pwlLang'))
        pwlDict = settings.get('spellchecker:pwlDict')
        self.ui.lineEditPWL.setText(pwlDict)

        tessExec = settings.get('tesseract-ocr:executable')
        self.ui.lnTessExec.setText(tessExec)
        tessData = settings.get('tesseract-ocr:TESSDATA_PREFIX:')
        self.ui.lnTessData.setText(tessData)

        self.ui.cbLog.setChecked(settings.get('log:errors'))
        self.ui.lnLog.setText(settings.get('log:filename'))


    @pyqtSignature('')
    def on_fontButton_clicked(self):
        ok = False
        editorFont, ok = QFontDialog.getFont(self.ui.fontLabel.font(),
                                      self, self.tr("Choose your font..."))
        if ok:
            self.changeFont(editorFont)

    @pyqtSignature('')
    def on_dictDirButton_clicked(self):
        dictDir = QFileDialog.getExistingDirectory(self,
                  self.tr("Choose your dictionary directory..."),
                  self.ui.directoryLine.text(),
                  QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly)

        if not dictDir.isEmpty():
            self.ui.directoryLine.setText(dictDir)
            self.langList(dictDir)

    @pyqtSignature('')
    def on_pushButtonPWL_clicked(self):
        filename = unicode(QFileDialog.getSaveFileName(self,
                self.tr("Select your private dictionary"),
                self.ui.lineEditPWL.text(),
                self.tr("Dictionary (*.txt *.dic);;All files (*);;")
                ))
        if not filename:
            return
        else:
            self.ui.lineEditPWL.setText(filename)

    @pyqtSignature('')
    def on_pbTessExec_clicked(self):
        fileFilter = self.tr("All files (*);;")
        if sys.platform == "win32":
            fileFilter = self.tr("Executables (*.exe);;") + fileFilter

        filename = unicode(QFileDialog.getOpenFileName(self,
                self.tr("Select tesseract-ocr executable..."),
                self.ui.lnTessExec.text(),
                fileFilter))
        if not filename:
            return
        else:
            self.ui.lnTessExec.setText(filename)

    @pyqtSignature('')
    def on_pbTessData_clicked(self):
        dictDir = QFileDialog.getExistingDirectory(self,
                  self.tr("Select Path Prefix To tessdata Directory..."),
                  self.ui.lnTessData.text(),
                  QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly)

        if not dictDir.isEmpty():
            self.ui.lnTessData.setText(dictDir)

    @pyqtSignature('')
    def on_pbLog_clicked(self):
        """ Select file for logging error/output of Lector
        """
        fileFilter = self.tr("Log files (*.log);;All files (*);;")
        init_filename = self.ui.lnLog.text()
        if not init_filename:
            if (os.path.split(sys.executable)[1]).lower().startswith('python'):
                logPath = os.path.abspath(os.path.dirname(__file__))
            else:
                logPath =  os.path.abspath(os.path.dirname(sys.executable))
            init_filename = os.path.join(logPath, "lector.log")
        filename = unicode(QFileDialog.getSaveFileName(self,
                self.tr("Select file for log output..."),
                init_filename,
                fileFilter))
        if not filename:
            return
        else:
            self.ui.lnLog.setText(filename)

    def accept(self):
        """ Store all settings
        """
        settings.set('scanner:height', self.ui.sbHeight.value())
        settings.set('scanner:width', self.ui.sbWidth.value())
        settings.set('scanner:resolution', self.ui.sbResolution.value())
        settings.set('scanner:mode',
                     self.colors[self.ui.combColor.currentIndex()])

        settings.set('editor:font', self.ui.fontLabel.font())
        settings.set('editor:clear', self.ui.checkBoxClear.isChecked())
        settings.set('editor:symbols', self.ui.symbolList.toPlainText())

        langIdx =  self.ui.dictBox.currentIndex()
        settings.set('spellchecker:lang', self.ui.dictBox.itemText(langIdx))
        settings.set('spellchecker:directory', self.ui.directoryLine.text())
        settings.set('spellchecker:pwlDict', self.ui.lineEditPWL.text())
        settings.set('spellchecker:pwlLang', self.ui.checkBoxPWL.isChecked())

        settings.set('tesseract-ocr:executable', self.ui.lnTessExec.text())
        settings.set('tesseract-ocr:TESSDATA_PREFIX',
                     self.ui.lnTessData.text())

        if self.ui.cbLog.isChecked():
            filename = self.ui.lnLog.text()
            if filename:
                # TODO(zdposter): check if file is writable
                pass
            else:
                QMessageBox.warning(self, self.tr("Lector"),
                    self.tr("You did not specified file for logging.\n") + \
                    self.tr("Logging will be disabled."), QMessageBox.Ok)
                self.ui.cbLog.setChecked(0)

        settings.set('log:errors', self.ui.cbLog.isChecked())
        settings.set('log:filename', self.ui.lnLog.text())

        uiLangIdx =  self.ui.cbLang.currentIndex()
        uiLocale = self.ui.cbLang.itemText(uiLangIdx)
        settings.set('ui:lang', uiLocale)

        self.settingAccepted.emit()
        QDialog.accept(self)


def main():
    """ Main loop to run text widget as applation
    """
    from PyQt4.QtGui import QApplication
    import ui.resources_rc

    app = QApplication(sys.argv)
    setting_dialog = Settings()
    setting_dialog.show()

    return app.exec_()

## MAIN
if __name__ == '__main__':
    sys.exit(main())