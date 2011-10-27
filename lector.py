#!/usr/bin/env python

""" Lector: lector.py

    Copyright (C) 2011 Davide Setti
    Website: http://code.google.com/p/lector

    This program is released under the GNU GPLv2
"""

## System
import sys
import os
from PyQt4.QtCore import SIGNAL, QObject, QSettings, QVariant, \
    QPoint, QSize, QString, QTime, qsrand, pyqtSignature, QLocale, \
    QTranslator
from PyQt4.QtGui import QMainWindow, QRadioButton, QFileDialog, \
    QMessageBox, QApplication, QComboBox

## Lector
from ui.ui_lector import Ui_Lector
from settingsdialog import Settings
from ocrwidget import QOcrWidget
from textwidget import TextWidget
from utils import get_tesseract_languages

class Window(QMainWindow):
    ocrAvailable = True
    thread = None

    def __init__(self, parent = None, scanner=True):
        QMainWindow.__init__(self)

        self.ui = Ui_Lector()
        self.ui.setupUi(self)

        self.ocrWidget = QOcrWidget("eng", 1, self.statusBar())
        self.textEditor = TextWidget()
        self.ui.textEditorDock.setWidget(self.textEditor)
        self.ocrWidget.textEditor = self.textEditor

        self.setCentralWidget(self.ocrWidget)

        self.statusBar().showMessage(self.tr("Ready"))
        QObject.connect(self.ui.actionRotateRight,
            SIGNAL("triggered()"), self.ocrWidget.rotateRight)
        QObject.connect(self.ui.actionRotateLeft,
            SIGNAL("triggered()"), self.ocrWidget.rotateLeft)
        QObject.connect(self.ui.actionRotateFull,
            SIGNAL("triggered()"), self.ocrWidget.rotateFull)
        QObject.connect(self.ui.actionZoomIn,
            SIGNAL("triggered()"), self.ocrWidget.zoomIn)
        QObject.connect(self.ui.actionZoomOut,
            SIGNAL("triggered()"), self.ocrWidget.zoomOut)
        QObject.connect(self.ui.actionOcr,
            SIGNAL("triggered()"), self.ocrWidget.doOcr)
        QObject.connect(self.ocrWidget.scene(),
            SIGNAL("changedSelectedAreaType(int)"),
            self.changedSelectedAreaType)

        try:
            languages = list(get_tesseract_languages())
        except TypeError: #tesseract is not installed
            #TODO: replace QMessageBox.warning with QErrorMessage (but we need
            #      to keep state
            #dialog = QErrorMessage(self)
            #dialog.showMessage(
            #    self.tr("tessaract not available. Please check requirements"))
            QMessageBox.warning(self,
                "Tesseract",
                self.tr("Tessaract not available. Please check requirements"))
            self.ocrAvailable = False
        else:
            languages.sort()

            languages_ext = {
                'bul': self.tr('Bulgarian'),
                'cat': self.tr('Catalan'),
                'ces': self.tr('Czech'),
                'chi_tra': self.tr('Chinese (Traditional)'),
                'chi_sim': self.tr('Chinese (Simplified)'),
                'dan': self.tr('Danish'),
                'dan-frak': self.tr('Danish (Fraktur)'),
                'nld': self.tr('Dutch'),
                'eng': self.tr('English'),
                'fin': self.tr('Finnish'),
                'fra': self.tr('French'),
                'deu': self.tr('German'),
                'deu-frak': self.tr('German (Fraktur)'),
                'ell': self.tr('Greek'),
                'hun': self.tr('Hungarian'),
                'ind': self.tr('Indonesian'),
                'ita': self.tr('Italian'),
                'jpn': self.tr('Japanese'),
                'kor': self.tr('Korean'),
                'lav': self.tr('Latvian'),
                'lit': self.tr('Lithuanian'),
                'nor': self.tr('Norwegian'),
                'pol': self.tr('Polish'),
                'por': self.tr('Portuguese'),
                'ron': self.tr('Romanian'),
                'rus': self.tr('Russian'),
                'slk': self.tr('Slovak'),
                'slk-frak': self.tr('Slovak (Fraktur)'),
                'slv': self.tr('Slovenian'),
                'spa': self.tr('Spanish'),
                'srp': self.tr('Serbian'),
                'swe': self.tr('Swedish'),
                'swe-frak': self.tr('Swedish (Fraktur)'),
                'tgl': self.tr('Tagalog'),
                'tur': self.tr('Turkish'),
                'ukr': self.tr('Ukrainian'),
                'vie': self.tr('Vietnamese')
                }

            for lang in languages:
                try:
                    lang_ext = languages_ext[lang]
                except KeyError:
                    continue

                self.ui.rbtn_lang_select.addItem(lang_ext, lang)
                QObject.connect(self.ui.rbtn_lang_select,
                    SIGNAL('currentIndexChanged(int)'), self.changeLanguage)

        #disable useless actions until a file has been opened
        self.enableActions(False)

        ## load saved settings
        self.readSettings()

        self.ui.actionScan.setEnabled(False)
        if scanner:
            self.on_actionChangeDevice_triggered()

    @pyqtSignature('')
    def on_actionChangeDevice_triggered(self):
        ##SANE
        try:
            import sane
        except ImportError:
            # sane found no scanner - disable scanning;
            print "Sane not found!"
        else:
            from scannerselect import ScannerSelect
            sane.init()
            sane_list = sane.get_devices()

            if not sane_list:
                # sane found scanner
                return

            ss = ScannerSelect(sane_list, parent=self)
            QObject.connect(ss, SIGNAL('accepted()'), self.scannerSelected)
            ss.show()

    def scannerSelected(self):
        self.ui.actionScan.setEnabled(True)

        if self.thread is None:
            from scannerthread import ScannerThread

            self.thread = ScannerThread(self)
            QObject.connect(self.thread, SIGNAL("scannedImage()"),
                            self.on_scannedImage)

    def on_scannedImage(self):
        self.ocrWidget.scene().im = self.thread.im
        self.ocrWidget.prepareDimensions()
        self.enableActions()

    @pyqtSignature('')
    def on_actionSettings_triggered(self):
        settings = Settings(self)
        QObject.connect(settings, SIGNAL('accepted()'),
                    self.updateTextEditor)
        settings.show()

    def updateTextEditor(self):
        self.textEditor.setEditorFont()

    @pyqtSignature('')
    def on_actionOpen_triggered(self):
        fn = unicode(QFileDialog.getOpenFileName(self,
                self.tr("Open image"), self.curDir,
                self.tr("Images (*.tif *.tiff *.png *.bmp *.jpg *.xpm)")
            ))
        if not fn: return

        self.ocrWidget.filename = fn
        self.curDir = os.path.dirname(fn)
        self.ocrWidget.cambiaImmagine()
        self.setWindowTitle("Lector: " + fn)

        self.enableActions(True)

    def enableActions(self, enable=True):
        for action in (self.ui.actionRotateRight,
                       self.ui.actionRotateLeft,
                       self.ui.actionRotateFull,
                       self.ui.actionZoomIn,
                       self.ui.actionZoomOut,
                       self.ui.actionSaveDocumentAs,
                       self.ui.actionSaveImageAs,):
            action.setEnabled(enable)
        self.ui.actionOcr.setEnabled(enable and self.ocrAvailable)

    @pyqtSignature('')
    def on_actionScan_triggered(self):
        self.thread.run()
        ##TODO: check thread end before the submission of a new task
        #self.thread.wait()

    def changeLanguage(self, row):
        lang = self.sender().itemData(row).toString()
        self.ocrWidget.language = lang

    @pyqtSignature('')
    def on_rbtn_text_clicked(self):
        self.ocrWidget.areaType = 1

    @pyqtSignature('')
    def on_rbtn_image_clicked(self):
        self.ocrWidget.areaType = 2

    # clicking the change box type events
    # from image type to text
    # or from text type to image
    @pyqtSignature('')
    def on_rbtn_areato_text_clicked(self):
        self.ocrWidget.scene().changeSelectedAreaType(1)

    @pyqtSignature('')
    def on_rbtn_areato_image_clicked(self):
        self.ocrWidget.scene().changeSelectedAreaType(2)

    def readSettings(self):
        settings = QSettings("Davide Setti", "Lector")
        pos = settings.value("pos", QVariant(QPoint(50, 50))).toPoint()
        size = settings.value("size", QVariant(QSize(800, 500))).toSize()
        self.curDir = settings.value("file_dialog_dir", QVariant('~/')
                                     ).toString()
        self.resize(size)
        self.move(pos)
        self.restoreGeometry(settings.value("mainWindowGeometry").toByteArray());
        self.restoreState(settings.value("mainWindowState").toByteArray());

        ## load saved language
        lang = str(settings.value("rbtn/lang", QVariant(QString())).toString())
        try:
            currentIndex=self.ui.rbtn_lang_select.findData(lang)
            self.ui.rbtn_lang_select.setCurrentIndex(currentIndex)
            self.ocrWidget.language = lang
        except KeyError:
            pass

    def writeSettings(self):
        from utils import settings

        settings.set("pos", self.pos())
        settings.set("size", self.size())
        settings.set("file_dialog_dir", self.curDir)
        settings.set("mainWindowGeometry", self.saveGeometry());
        settings.set("mainWindowState", self.saveState());

        ## save language
        settings.set("rbtn/lang", self.ocrWidget.language)

    def closeEvent(self, event):
        if (not self.ocrWidget.scene().isModified) or self.areYouSureToExit():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

    def areYouSureToExit(self):
        ret = QMessageBox.warning(self, "Lector",
                                  self.tr("Are you sure you want to exit?"),
                                  QMessageBox.Yes | QMessageBox.No)
        return ret == QMessageBox.Yes

    @pyqtSignature('')
    def on_actionSaveDocumentAs_triggered(self):
        fn = unicode(QFileDialog.getSaveFileName(self,
                                        self.tr("Save document"), self.curDir,
                                        self.tr("ODT document (*.odt);;Text file (*.txt);;HTML file (*.html)")
                                        ))
        if not fn: return

        self.curDir = os.path.dirname(fn)
        self.textEditor.saveAs(fn)

    @pyqtSignature('')
    def on_actionSaveImageAs_triggered(self):
        fn = unicode(QFileDialog.getSaveFileName(self,
                                            self.tr("Save image"), self.curDir,
                                            self.tr("PNG image (*.png);;TIFF image (*.tif *.tiff);;BMP image (*.bmp)")
                                            ))
        if not fn: return

        self.curDir = os.path.dirname(fn)
        ## TODO: move this to the Scene?
        ## TODO: if im is a jpeg, will pil convert it?
        self.ocrWidget.scene().im.save(fn)
        #self.textEditor.saveAs(fn)

    @pyqtSignature('')
    def on_actionAbout_Lector_triggered(self):
        QMessageBox.about(self, self.tr("About Lector"), self.tr(
          "<p>The <b>Lector</b> is a graphical ocr solution for GNU/"
          "Linux and Windows based on Python, Qt4 and tessaract OCR.</p>"
          "<p>Scanning option is available only on GNU/Linux via SANE.</p><p></p>"
          "<p><b>Author:</b> Davide Setti</p><p></p>"
          "<p><b>Contributors:</b> chopinX04, filip.dominec, zdposter</p>"
          "<p><b>Web site:</b> http://code.google.com/p/lector</p>"
          "<p><b>Source code:</b> http://code.google.com/p/lector/source/checkout</p>"))

    def changedSelectedAreaType(self, _type):
        if _type in (1,2):
            self.ui.rbtn_areato_text.setCheckable(True)
            self.ui.rbtn_areato_image.setCheckable(True)

            if _type == 1:
                self.ui.rbtn_areato_text.setChecked(True)
            else: #_type = 2
                self.ui.rbtn_areato_image.setChecked(True)
        else:
            self.ui.rbtn_areato_text.setCheckable(False)
            self.ui.rbtn_areato_text.update()
            self.ui.rbtn_areato_image.setCheckable(False)
            self.ui.rbtn_areato_image.update()


## MAIN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    opts = [str(arg) for arg in app.arguments()[1:]]
    if '--no-scanner' in opts:
        scanner = False
    else:
        scanner = True
    qsrand(QTime(0, 0, 0).secsTo(QTime.currentTime()))

    locale = QLocale.system().name()
    lecTranslator = QTranslator()
    if lecTranslator.load(":/translations/ts/lector_" + locale, 'ts'):
        app.installTranslator(lecTranslator)

    qtTranslator = QTranslator()
    if qtTranslator.load("qt_" + locale, 'ts'):
        app.installTranslator(qtTranslator)

    window = Window(scanner=scanner)

    window.show()

    sys.exit(app.exec_())
