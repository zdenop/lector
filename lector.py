#!/usr/bin/env python

""" Lector: lector.py

    Copyright (C) 2011 Davide Setti
    Website: http://code.google.com/p/lector

    This program is released under the GNU GPLv2
"""

## System
import  sys
import  os
from    PyQt4.QtCore  import SIGNAL, QObject, QSettings, QVariant, \
        QPoint, QSize, QString, QTime, qsrand, pyqtSignature, QLocale, \
        QTranslator
from    PyQt4.QtGui   import QMainWindow, QRadioButton, QFileDialog, \
        QMessageBox, QApplication, QComboBox
from    subprocess    import Popen, PIPE
from    glob          import glob

## Lector
from    ui_lector     import Ui_Lector
from    ocrwidget     import QOcrWidget
from    textwidget    import TextWidget
from    scannerselect import ScannerSelect
from    scannerthread import ScannerThread


class Window(QMainWindow):
    ## Override constructor
    ## 
    def __init__(self, parent = None):
        QMainWindow.__init__(self)

        self.ui = Ui_Lector()
        self.ui.setupUi(self)

        self.ocrWidget = QOcrWidget("eng", 1, self.statusBar())
        self.textBrowser = TextWidget()
        self.ui.textBrowserDock.setWidget(self.textBrowser)
        self.ocrWidget.textBrowser = self.textBrowser

        self.setCentralWidget(self.ocrWidget)

        self.statusBar().showMessage(self.tr("Ready"))
        QObject.connect(self.ui.actionRotateRight,
            SIGNAL("activated()"), self.ocrWidget.rotateRight)
        QObject.connect(self.ui.actionRotateLeft,
            SIGNAL("activated()"), self.ocrWidget.rotateLeft)
        QObject.connect(self.ui.actionRotateFull,
            SIGNAL("activated()"), self.ocrWidget.rotateFull)
        QObject.connect(self.ui.actionZoomIn,
            SIGNAL("activated()"), self.ocrWidget.zoomIn)
        QObject.connect(self.ui.actionZoomOut,
            SIGNAL("activated()"), self.ocrWidget.zoomOut)
        QObject.connect(self.ui.actionOcr,
            SIGNAL("activated()"), self.ocrWidget.doOcr)

        ## TODO: check if tesseract is installed
        poTess = Popen('tesseract try try -l iamnottrue', stderr=PIPE,
            shell=True)
        lTess = poTess.stderr.readline()
        langdata_ext = lTess.split('/').pop().strip().rsplit('.', 1)[1]
        if os.getenv('TESSDATA_PREFIX') is None:
            pTess = '/' + '/'.join((lTess.split('/'))[1:-1]) + '/'
        else:
            pTess = os.getenv('TESSDATA_PREFIX') + "tessdata/"

        langdata = glob(pTess + '*.' + langdata_ext)
        languages = [os.path.basename(uc).rsplit('.', 1)[0] for uc in langdata]
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

            ##TODO:change this layout to a more human name
            self.ui.rbtn_lang_select.addItem(lang_ext, QVariant(lang))
            QObject.connect(self.ui.rbtn_lang_select,
                SIGNAL('currentIndexChanged(int)'), self.changeLanguage)

        #disable useless actions until a file has been opened
        self.enableActions(False)

        ## load saved settings
        self.readSettings()

        self.check_scanner_env()


    def check_scanner_env(self):
        ##SANE
        try:
            import sane
            sane.init()
            sane_list = sane.get_devices()

            if sane_list:  # sane found scanner
                #TODO: if one scanner - automatically select
                scanner_desc_list = [scanner[2] for scanner in sane_list]

                ss = ScannerSelect()
                idx = ss.getSelectedIndex(self.tr('Select scanner'),
                                          scanner_desc_list, 0)
                try:
                    self.selectedScanner = sane_list[idx][0]
                except KeyError:
                    self.ui.actionScan.setEnabled(False)
                else:
                    self.thread = ScannerThread(self, self.selectedScanner)
                    QObject.connect(self.thread, SIGNAL("scannedImage()"),
                                    self.on_scannedImage)

            else: # sane found no scanner - disable scanning;
                print "No scanner found!"
                self.ui.actionScan.setEnabled(False)
        except:
            self.ui.actionScan.setEnabled(False)


    def on_scannedImage(self):
        im = self.thread.im
        self.ocrWidget.scene().im = im
        self.ocrWidget.prepareDimensions()
        self.enableActions()

    @pyqtSignature('')
    def on_actionOpen_activated(self):
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
                       self.ui.actionOcr,
                       self.ui.actionSaveDocumentAs,
                       self.ui.actionSaveImageAs,):
            action.setEnabled(enable)

    @pyqtSignature('')
    def on_actionScan_activated(self):
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

    def readSettings(self):
        settings = QSettings("Davide Setti", "Lector")
        pos = settings.value("pos", QVariant(QPoint(50, 50))).toPoint()
        size = settings.value("size", QVariant(QSize(800, 500))).toSize()
        self.curDir = settings.value("file_dialog_dir", QVariant('~/')
                                     ).toString()
        self.resize(size)
        self.move(pos)

        ## load saved language
        lang = str(settings.value("rbtn/lang", QVariant(QString())).toString())
        try:
            currentIndex=self.ui.rbtn_lang_select.findData(lang)
            self.ui.rbtn_lang_select.setCurrentIndex(currentIndex)
            self.ocrWidget.language = lang
        except KeyError:
            pass

        #TODO: ridimensionamento della dock non funziona
        #pos = settings.value("textbrowser/pos").toPoint()
        #size = settings.value("textbrowser/size", QVariant(QSize(200, 200))
        #        ).toSize()
        #self.ui.textBrowser.resize(size)
        #self.ui.textBrowser.move(pos)

    def writeSettings(self):
        settings = QSettings("Davide Setti", "Lector")
        settings.setValue("pos", QVariant(self.pos()))
        settings.setValue("size", QVariant(self.size()))
        settings.setValue("file_dialog_dir", QVariant(self.curDir))
        #settings.setValue("textbrowser/pos", QVariant(
        #            self.ui.textBrowserDock.pos()))
        #settings.setValue("textbrowser/size", QVariant(
        #            self.ui.textBrowserDock.size()))

        ## save language
        settings.setValue("rbtn/lang", QVariant(self.ocrWidget.language))

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
        if ret == QMessageBox.No:
            return False
        elif ret == QMessageBox.Yes:
            return True

    @pyqtSignature('')
    def on_actionSaveDocumentAs_activated(self):
        fn = unicode(QFileDialog.getSaveFileName(self,
                                        self.tr("Save document"), self.curDir,
                                        self.tr("RTF document") + " (*.rtf)"
                                        ))
        if not fn: return

        self.curDir = os.path.dirname(fn)
        self.textBrowser.saveAs(fn)

    @pyqtSignature('')
    def on_actionSaveImageAs_activated(self):
        fn = unicode(QFileDialog.getSaveFileName(self,
                                            self.tr("Save image"), self.curDir,
                                            self.tr("PNG image") + " (*.png)"
                                            ))
        if not fn: return

        self.curDir = os.path.dirname(fn)
        ## TODO: move this to the Scene?
        ## TODO: if jpeg pil converts it??
        self.ocrWidget.im.save(fn)
        #self.textBrowser.saveAs(fn)

    @pyqtSignature('')
    def on_actionAbout_Lector_activated(self):
        QMessageBox.about(self, self.tr("About Lector"), self.tr(
          "<p>The <b>Lector</b> is a graphical ocr solution for GNU/"
          "Linux based on Python, Qt4 and tessaract OCR.</p><p></p>"
          "<p><b>Author:</b> Davide Setti</p><p></p>"
          "<p><b>Contributors:</b> chopinX04, filip.dominec, zdposter</p>"
          "<p><b>Web site:</b> http://code.google.com/p/lector</p>"
          "<p><b>Source code:</b> http://code.google.com/p/lector/source/checkout</p>"))


## MAIN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    qsrand(QTime(0, 0, 0).secsTo(QTime.currentTime()))

    ## TODO: check for settings first. If they do not exists initialize them!
    locale = QLocale.system().name()
    lecTranslator = QTranslator()
    if lecTranslator.load("lector_" + locale, 'ts'):
        app.installTranslator(lecTranslator)

    qtTranslator = QTranslator()
    if qtTranslator.load("qt_" + locale, 'ts'):
        app.installTranslator(qtTranslator)

    window = Window()

    window.show()
    sys.exit(app.exec_())
