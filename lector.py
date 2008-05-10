#!/usr/bin/env python

""" Lector: lector.py

    Copyright (C) 2008 Davide Setti

    This program is released under the GNU GPLv2
"""


import sys
import os
#from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_lector import Ui_Lector
from ocrwidget import QOcrWidget
from textwidget import TextWidget


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
        self.readSettings()
        QObject.connect(self.ui.actionOpen,SIGNAL("activated()"), self.openImage)
        QObject.connect(self.ui.actionRotateRight,SIGNAL("activated()"), self.ocrWidget.rotateRight)
        QObject.connect(self.ui.actionRotateLeft,SIGNAL("activated()"), self.ocrWidget.rotateLeft)
        QObject.connect(self.ui.actionRotateFull,SIGNAL("activated()"), self.ocrWidget.rotateFull)
        QObject.connect(self.ui.actionZoomIn,SIGNAL("activated()"), self.ocrWidget.zoomIn)
        QObject.connect(self.ui.actionZoomOut,SIGNAL("activated()"), self.ocrWidget.zoomOut)
        QObject.connect(self.ui.actionOcr,SIGNAL("activated()"), self.ocrWidget.doOcr)
        QObject.connect(self.ui.actionSaveAs,SIGNAL("activated()"), self.saveAs)

        ## TODO: use only a function for this
        QObject.connect(self.ui.rbtn_ita,SIGNAL("clicked()"), self.change_language_ita)
        QObject.connect(self.ui.rbtn_deu,SIGNAL("clicked()"), self.change_language_deu)
        QObject.connect(self.ui.rbtn_eng,SIGNAL("clicked()"), self.change_language_eng)

        QObject.connect(self.ui.rbtn_text,SIGNAL("clicked()"), self.change_ocr_area_text)
        QObject.connect(self.ui.rbtn_image,SIGNAL("clicked()"), self.change_ocr_area_image)

        #disable unusable actions until a file has been opened
        self.ui.actionRotateRight.setEnabled(False)
        self.ui.actionRotateLeft.setEnabled(False)
        self.ui.actionRotateFull.setEnabled(False)
        self.ui.actionZoomIn.setEnabled(False)
        self.ui.actionZoomOut.setEnabled(False)
        self.ui.actionOcr.setEnabled(False)
        self.ui.actionSaveAs.setEnabled(False)


    def openImage(self):
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


    def change_language_ita(self):
        self.ocrWidget.language = "ita"


    def change_language_deu(self):
        self.ocrWidget.language = "deu"


    def change_language_eng(self):
        self.ocrWidget.language = "eng"


    def change_ocr_area_text(self):
        self.ocrWidget.areaType = 1


    def change_ocr_area_image(self):
        self.ocrWidget.areaType = 2


    def readSettings(self):
        settings = QSettings("Davide Setti", "Lector");
        pos = settings.value("pos", QVariant(QPoint(50, 50))).toPoint()
        size = settings.value("size", QVariant(QSize(800, 500))).toSize()
        self.curDir = settings.value("file_dialog_dir", QVariant('~/')).toString()
        self.resize(size)
        self.move(pos)
        
        ## load saved language
        lang = settings.value("rbtn/lang", QVariant(QString())).toString()
        if lang:
            s = "self.ui.rbtn_%s.setChecked(True)" % lang
            exec(s)
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


    def saveAs(self):
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
