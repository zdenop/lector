from PyQt4.QtGui import QDialog, QFontDialog, QFont
from PyQt4.QtCore import pyqtSignature

from ui.ui_settings import Ui_Settings
from utils import settings

class Settings(QDialog):
    colors = ['Color', 'Gray', 'Lineart']

    def __init__(self, parent = None):
        QDialog.__init__(self, parent)

        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.initSettings()

    def changeFont(self, editorFont):
        self.ui.fontLabel.setFont(editorFont)
        label = editorFont.family().toAscii().data()
        label += ", %d pt" % editorFont.pointSize()
        self.ui.fontLabel.setText(label)

    def initSettings(self):
        self.ui.sbHeight.setValue(settings.get('scanner:height'))
        self.ui.sbWidth.setValue(settings.get('scanner:width'))
        self.ui.sbResolution.setValue(settings.get('scanner:resolution'))
        self.ui.combColor.setCurrentIndex(
            self.colors.index(settings.get('scanner:mode')))

        self.changeFont(QFont(settings.get('editor:font')))


    @pyqtSignature('')
    def on_fontButton_clicked(self):
        ok = False
        editorFont, ok=QFontDialog.getFont(self.ui.fontLabel.font(),
                                      self, u"Choose your font!")
        if ok:
            self.changeFont(editorFont)

    def accept(self):
        settings.set('scanner:height', self.ui.sbHeight.value())
        settings.set('scanner:width', self.ui.sbWidth.value())
        settings.set('scanner:resolution', self.ui.sbResolution.value())
        settings.set('scanner:mode',
                     self.colors[self.ui.combColor.currentIndex()])

        settings.set('editor:font', self.ui.fontLabel.font())

        QDialog.accept(self)

    def reject(self):
        super(Settings, self).hide()
