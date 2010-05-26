#!/usr/bin/env python
# vim: set foldlevel=1:

""" Lector: lector.py

    Copyright (C) 2008-2010 Davide Setti

    This program is released under the GNU GPLv2
"""

## System
import  sys
import  os
from    PyQt4.QtCore  import *
from    PyQt4.QtGui   import *
from    subprocess    import Popen, PIPE
from    glob          import glob
import  sane

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

        poTess = Popen('tesseract /tmp/try /tmp/try -l iamnottrue', stderr=PIPE,
            shell=True)
        lTess = poTess.stderr.readline()
        pTess = '/' + '/'.join((lTess.split('/'))[1:-1]) + '/'

        unicharsets = glob(pTess+'*.unicharset')
        languages = [uc[len(pTess):len(pTess)+3] for uc in unicharsets]

        languages_ext = {
            'eng': self.tr('English'),
            'ita': self.tr('Italian'), 'deu': self.tr('German'),
            'nld': self.tr('Dutch'), 'fra': self.tr('French'),
            'spa': self.tr('Spanish')}
        self.rbtn_languages = {}

        for lang in languages:
            try:
                lang_ext = languages_ext[lang]
            except KeyError:
                continue
            
            rbtn = QRadioButton(self.ui.groupBox_language)
            rbtn.setObjectName("rbtn_%s" % lang)
            rbtn.setText(lang_ext)
            
            ##TODO:change this layout to a more human name
            self.ui.vboxlayout2.addWidget(rbtn)

            QObject.connect(rbtn, SIGNAL('clicked()'), self.changeLanguage)

            self.rbtn_languages[lang] = rbtn

        #disable unusable actions until a file has been opened
        self.enableActions(False)

        ## load saved settings
        self.readSettings()

        ##SANE
        sane.init()
        sane_list = sane.get_devices()
        scanner_desc_list = [scanner[2] for scanner in sane_list]

        ss = ScannerSelect()

        idx = ss.getSelectedIndex(self.tr('Select scanner'),
                                  scanner_desc_list, 0)
        if idx > -1:
            self.selectedScanner = sane.get_devices()[idx][0]
            self.thread = ScannerThread(self, self.selectedScanner)
            
            QObject.connect(self.thread, SIGNAL("scannedImage()"),
                            self.on_scannedImage)
        else:
            self.ui.actionScan.setEnabled(False)
        

    def on_scannedImage(self):
        print "scanned"
        im = self.thread.im
        self.ocrWidget.scene().im = im
        self.ocrWidget.prepareDimensions()
        self.enableActions()

    @pyqtSignature('')
    def on_actionOpen_activated(self):
        fn = unicode(QFileDialog.getOpenFileName(self,
                self.tr("Open image"), self.curDir,
                self.tr("Images (*.png *.xpm *.jpg)")
            ))
        if fn:
            self.ocrWidget.filename = fn
            self.curDir = os.path.dirname(fn)
            self.ocrWidget.cambiaImmagine()

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

    def changeLanguage(self):
        lang = self.sender().objectName()[5:]
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
        if lang and self.rbtn_languages.has_key(lang):
            self.rbtn_languages[lang].setChecked(True)
            self.ocrWidget.language = lang

        #TODO: ridimensionamento della dock non funziona
        #pos = settings.value("textbrowser/pos").toPoint()
        #size = settings.value("textbrowser/size", QVariant(QSize(200, 200))).toSize()
        #self.ui.textBrowser.resize(size)
        #self.ui.textBrowser.move(pos)


    def writeSettings(self):
        settings = QSettings("Davide Setti", "Lector")
        settings.setValue("pos", QVariant(self.pos()))
        settings.setValue("size", QVariant(self.size()))
        settings.setValue("file_dialog_dir", QVariant(self.curDir))
        #settings.setValue("textbrowser/pos", QVariant(self.ui.textBrowserDock.pos()))
        #settings.setValue("textbrowser/size", QVariant(self.ui.textBrowserDock.size()))

        ## save language
        settings.setValue("rbtn/lang", QVariant(self.ocrWidget.language))


    def closeEvent(self, event):
        if (not self.ocrWidget.scene().isModified) or self.areYouSureToExit():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

    
    def areYouSureToExit(self):
        #if (textEdit->document()->isModified()) {
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
        if fn:
            self.curDir = os.path.dirname(fn)
            self.textBrowser.saveAs(fn)

    
    @pyqtSignature('')
    def on_actionSaveImageAs_activated(self):
        fn = unicode(QFileDialog.getSaveFileName(self,
                                            self.tr("Save image"), self.curDir,
                                            self.tr("PNG document") + " (*.png)"
                                            ))
        if fn:
            self.curDir = os.path.dirname(fn)
            ## TODO: move this to the Scene?
            ## TODO: if jpeg pil converts it??
            self.ocrWidget.im.save(fn)
            #self.textBrowser.saveAs(fn)


## MAIN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    qsrand(QTime(0,0,0).secsTo(QTime.currentTime()))

    locale = QLocale.system().name()
    lecTranslator = QTranslator()
    if lecTranslator.load("lector_" + locale, ':/translations/ts'):
        app.installTranslator(lecTranslator)

    qtTranslator = QTranslator()
    if qtTranslator.load("qt_" + locale, ':/translations/ts'):
        app.installTranslator(qtTranslator)

    window = Window()

    window.show()

    sys.exit(app.exec_())
