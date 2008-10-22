#!/usr/bin/env python

""" Lector: lector.py

    Copyright (C) 2008 Davide Setti

    This program is released under the GNU GPLv2
"""


import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_lector import Ui_Lector
from ocrwidget import QOcrWidget
from textwidget import TextWidget
from subprocess import Popen, PIPE
from glob import glob

class Window(QMainWindow):
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
        QObject.connect(self.ui.actionRotateRight,SIGNAL("activated()"), self.ocrWidget.rotateRight)
        QObject.connect(self.ui.actionRotateLeft,SIGNAL("activated()"), self.ocrWidget.rotateLeft)
        QObject.connect(self.ui.actionRotateFull,SIGNAL("activated()"), self.ocrWidget.rotateFull)
        QObject.connect(self.ui.actionZoomIn,SIGNAL("activated()"), self.ocrWidget.zoomIn)
        QObject.connect(self.ui.actionZoomOut,SIGNAL("activated()"), self.ocrWidget.zoomOut)
        QObject.connect(self.ui.actionOcr,SIGNAL("activated()"), self.ocrWidget.doOcr)

        self.findInstalledLanguages()

        #disable unusable actions until a file has been opened
        self.ui.actionRotateRight.setEnabled(False)
        self.ui.actionRotateLeft.setEnabled(False)
        self.ui.actionRotateFull.setEnabled(False)
        self.ui.actionZoomIn.setEnabled(False)
        self.ui.actionZoomOut.setEnabled(False)
        self.ui.actionOcr.setEnabled(False)
        self.ui.actionSaveAs.setEnabled(False)
        
        ## load saved settings
        self.readSettings()

    
    def findInstalledLanguages(self):
        self.rbtn_languages = {}
        try:
            Popen('tesseract', shell=False, stderr=PIPE)
        except OSError, e:
            print self.tr('Tesseract is not installed')
            QMessageBox.critical(self, self.tr('Tesseract is not installed'), self.tr('This program needs tesseract, but it\'s not installed on this system\nLector will be started, but it won\'t be able to do OCR!'))
            return

        poTess = Popen('tesseract /tmp/prova /tmp/prova -l iamnottrue', stderr=PIPE, shell=True)
        lTess = poTess.stderr.readline()
        pTess = '/' + '/'.join((lTess.split('/'))[1:-1]) + '/'

        languages = list()
        unicharsets = glob(pTess+'*.unicharset')
        for uc in unicharsets:
            languages.append(uc[len(pTess):len(pTess)+3])

        languages_ext = {'eng': self.tr('English'),
            'ita': self.tr('Italian'), 'deu': self.tr('German'), 'spa': self.tr('Spanish')}

        for lang in languages:
            rbtn = QRadioButton(self.ui.groupBox_language)
            rbtn.setObjectName("rbtn_%s" % lang)
            rbtn.setText(languages_ext[lang])
            
            ##TODO:change this layout to a more human name
            self.ui.vboxlayout2.addWidget(rbtn)

            QObject.connect(rbtn, SIGNAL('clicked()'), self.changeLanguage)

            self.rbtn_languages[lang] = rbtn


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

            self.ui.actionRotateRight.setEnabled(True)
            self.ui.actionRotateLeft.setEnabled(True)
            self.ui.actionRotateFull.setEnabled(True)
            self.ui.actionZoomIn.setEnabled(True)
            self.ui.actionZoomOut.setEnabled(True)
            self.ui.actionOcr.setEnabled(True)
            self.ui.actionSaveAs.setEnabled(True)


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
        settings = QSettings("Davide Setti", "Lector");
        pos = settings.value("pos", QVariant(QPoint(50, 50))).toPoint()
        size = settings.value("size", QVariant(QSize(800, 500))).toSize()
        self.curDir = settings.value("file_dialog_dir", QVariant('~/')).toString()
        self.resize(size)
        self.move(pos)
        
        ## load saved language
        lang = str(settings.value("rbtn/lang", QVariant(QString())).toString())
        if lang and lang in self.rbtn_languages:
            ## TODO: if the language is not installed anymore?
            self.rbtn_languages[lang].setChecked(True)
            self.ocrWidget.language = lang

        #TODO: ridimensionamento della dock non funziona
        #pos = settings.value("textbrowser/pos").toPoint()
        #size = settings.value("textbrowser/size", QVariant(QSize(200, 200))).toSize()
        #print size.width()
        #print pos.x()
        #self.ui.textBrowser.resize(size)
        #self.ui.textBrowser.move(pos)
        #print self.ui.textBrowserDock.size().width()


    def writeSettings(self):
        settings = QSettings("Davide Setti", "Lector")
        settings.setValue("pos", QVariant(self.pos()))
        settings.setValue("size", QVariant(self.size()))
        settings.setValue("file_dialog_dir", QVariant(self.curDir))
        #settings.setValue("textbrowser/pos", QVariant(self.ui.textBrowserDock.pos()))
        #settings.setValue("textbrowser/size", QVariant(self.ui.textBrowserDock.size()))

        ## save language
        settings.setValue("rbtn/lang",
                QVariant(self.ocrWidget.language))


    def closeEvent(self, event):
        if (not self.ocrWidget.isModified) or self.areYouSureToExit():
                self.writeSettings()
                event.accept()
        else:
                event.ignore()

    
    def areYouSureToExit(self):
        #if (textEdit->document()->isModified()) {
        ret = QMessageBox.warning(self, "Lector", self.tr("Are you sure you want to exit?"), QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.No:
            return False
        elif ret == QMessageBox.Yes:
            return True


    @pyqtSignature('')
    def on_actionSaveAs_activated(self):
        fn = unicode(QFileDialog.getSaveFileName(self,
                                            self.tr("Save document"), self.curDir,
                                            self.tr("RTF document") + " (*.rtf)"
                                            ))
        if fn:
            self.curDir = os.path.dirname(fn)
            self.textBrowser.saveAs(fn)



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
