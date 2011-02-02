from PyQt4.QtGui import QDialog

from ui.ui_settings import Ui_Settings
from utils import settings

class Settings(QDialog):
    colors = ['Color', 'Gray', 'Lineart']

    def __init__(self, parent = None):
        QDialog.__init__(self, parent)

        self.ui = Ui_Settings()
        self.ui.setupUi(self)

        self.ui.sbHeight.setValue(settings.get('scanner:height'))
        self.ui.sbWidth.setValue(settings.get('scanner:width'))
        self.ui.sbResolution.setValue(settings.get('scanner:resolution'))
        self.ui.combColor.setCurrentIndex(
            self.colors.index(settings.get('scanner:mode'))
        )


    def accept(self):
        settings.set('scanner:height', self.ui.sbHeight.value())
        settings.set('scanner:width', self.ui.sbWidth.value())
        settings.set('scanner:resolution', self.ui.sbResolution.value())
        settings.set('scanner:mode',
                     self.colors[self.ui.combColor.currentIndex()])

        QDialog.accept(self)

