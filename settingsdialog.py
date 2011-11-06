from PyQt4.QtGui import QDialog, QFontDialog, QFont, QFileDialog
from PyQt4.QtCore import pyqtSignature

from ui.ui_settings import Ui_Settings
from utils import settings
from utils import get_spellchecker_languages

class Settings(QDialog):
    colors = ['Color', 'Gray', 'Lineart']

    def __init__(self, parent = None, tabIndex = 0):
        QDialog.__init__(self, parent)

        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.ui.tabWidget.setCurrentIndex(tabIndex); 
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
            self.ui.spellInfoLabel.setText(self.tr("Enchant not found. Check if pyenchant is installed!"))
        elif len(langs) == 0:
            self.ui.spellInfoLabel.setText(self.tr("Enchant found. Check your dictionary directory."))
        else:
            for lang in langs:
                self.ui.dictBox.addItem(lang)

            spellLang = settings.get('spellchecker:lang')
            try:
                currentIndex=self.ui.dictBox.findText(spellLang)
                self.ui.dictBox.setCurrentIndex(currentIndex)
            except KeyError:
                print "'%s' was not found in available dictionaries." % spellLang

    def initSettings(self):
        self.ui.sbHeight.setValue(settings.get('scanner:height'))
        self.ui.sbWidth.setValue(settings.get('scanner:width'))
        self.ui.sbResolution.setValue(settings.get('scanner:resolution'))
        self.ui.combColor.setCurrentIndex(
            self.colors.index(settings.get('scanner:mode')))

        self.changeFont(QFont(settings.get('editor:font')))
        self.ui.checkBoxClear.setChecked(settings.get('editor:clear'))

        spellDictDir = settings.get('spellchecker:directory')
        self.ui.directoryLine.setText(spellDictDir)
        self.langList(spellDictDir)

    @pyqtSignature('')
    def on_fontButton_clicked(self):
        ok = False
        editorFont, ok=QFontDialog.getFont(self.ui.fontLabel.font(),
                                      self, self.tr("Choose your font..."))
        if ok:
            self.changeFont(editorFont)

    @pyqtSignature('')
    def on_dictDirButton_clicked(self):
        dir = QFileDialog.getExistingDirectory(self,
                  self.tr("Choose your dictionary directory..."),
                  self.ui.directoryLine.text(),
                  QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly)

        if not dir.isEmpty():
            self.ui.directoryLine.setText(dir)
            self.langList(dir)

    def accept(self):
        settings.set('scanner:height', self.ui.sbHeight.value())
        settings.set('scanner:width', self.ui.sbWidth.value())
        settings.set('scanner:resolution', self.ui.sbResolution.value())
        settings.set('scanner:mode',
                     self.colors[self.ui.combColor.currentIndex()])

        settings.set('editor:font', self.ui.fontLabel.font())
        settings.set('editor:clear', self.ui.checkBoxClear.isChecked())

        langIdx =  self.ui.dictBox.currentIndex()
        settings.set('spellchecker:lang', self.ui.dictBox.itemText(langIdx))
        settings.set('spellchecker:directory', self.ui.directoryLine.text())

        QDialog.accept(self)

