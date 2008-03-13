#!/usr/bin/env python

""" Lector: lector.py

    Copyright (C) 2008 Davide Setti

    This program is released under the GNU GPLv2
"""


import sys
from PyQt4 import QtCore, QtGui
from ui_lector import Ui_Lector
from ocrwidget import QOcrWidget
from textwidget import TextWidget

class Window(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_Lector()
        self.ui.setupUi(self)

        self.ocrWidget = QOcrWidget()
        self.ocrWidget.statusBar = self.statusBar()
        self.ocrWidget.language = "ita"
        self.textBrowser = TextWidget()
        self.ui.textBrowserDock.setWidget(self.textBrowser)
        self.ocrWidget.textBrowser = self.textBrowser

        self.setCentralWidget(self.ocrWidget)

        self.statusBar().showMessage(self.tr("Ready"))
        self.readSettings()
        QtCore.QObject.connect(self.ui.actionOpen,QtCore.SIGNAL("activated()"), self.openImage)
        QtCore.QObject.connect(self.ui.actionRotateRight,QtCore.SIGNAL("activated()"), self.ocrWidget.rotateRight)
        QtCore.QObject.connect(self.ui.actionRotateLeft,QtCore.SIGNAL("activated()"), self.ocrWidget.rotateLeft)
        QtCore.QObject.connect(self.ui.actionRotateFull,QtCore.SIGNAL("activated()"), self.ocrWidget.rotateFull)
        QtCore.QObject.connect(self.ui.actionZoomIn,QtCore.SIGNAL("activated()"), self.ocrWidget.zoomIn)
        QtCore.QObject.connect(self.ui.actionZoomOut,QtCore.SIGNAL("activated()"), self.ocrWidget.zoomOut)
        QtCore.QObject.connect(self.ui.actionOcr,QtCore.SIGNAL("activated()"), self.ocrWidget.doOcr)
        QtCore.QObject.connect(self.ui.actionSaveAs,QtCore.SIGNAL("activated()"), self.saveAs)

        QtCore.QObject.connect(self.ui.rbtn_ita,QtCore.SIGNAL("clicked()"), self.change_language_ita)
        QtCore.QObject.connect(self.ui.rbtn_deu,QtCore.SIGNAL("clicked()"), self.change_language_deu)
        QtCore.QObject.connect(self.ui.rbtn_eng,QtCore.SIGNAL("clicked()"), self.change_language_eng)


    def openImage(self):
        #fd = QtGui.QFileDialog(self,QtCore.QString('Apri immagine'),QtCore.QString('/home/'))
        self.ocrWidget.filename = unicode(QtGui.QFileDialog.getOpenFileName(self,
                                            "Apri immagine", "/home",
                                            "Immagini (*.png *.xpm *.jpg)"
                                            ))
        self.ocrWidget.cambiaImmagine()


    def change_language_ita(self):
        self.ocrWidget.language = "ita"


    def change_language_deu(self):
        self.ocrWidget.language = "deu"


    def change_language_eng(self):
        self.ocrWidget.language = "eng"

    def readSettings(self):
        settings = QtCore.QSettings("Davide Setti", "Lector");
        pos = settings.value("pos", QtCore.QVariant(QtCore.QPoint(50, 50))).toPoint()
        size = settings.value("size", QtCore.QVariant(QtCore.QSize(800, 500))).toSize()
        self.resize(size)
        self.move(pos)
        
        #TODO: ridimensionamento della dock non funziona
        #pos = settings.value("textbrowser/pos").toPoint()
        #size = settings.value("textbrowser/size", QtCore.QVariant(QtCore.QSize(200, 200))).toSize()
        #print size.width()
        #print pos.x()
        #self.ui.textBrowser.resize(size)
        #self.ui.textBrowser.move(pos)
        #print self.ui.textBrowserDock.size().width()


    def writeSettings(self):
        settings = QtCore.QSettings("Davide Setti", "Lector")
        settings.setValue("pos", QtCore.QVariant(self.pos()))
        settings.setValue("size", QtCore.QVariant(self.size()))
        #settings.setValue("textbrowser/pos", QtCore.QVariant(self.ui.textBrowserDock.pos()))
        #settings.setValue("textbrowser/size", QtCore.QVariant(self.ui.textBrowserDock.size()))

    def closeEvent(self, event):
        if self.areYouSureToExit():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

    
    def areYouSureToExit(self):
        #if (textEdit->document()->isModified()) {
        ret = QtGui.QMessageBox.warning(self, "Lector", "Sei sicuro di voler uscire?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return False
        elif ret == QtGui.QMessageBox.Yes:
            return True


    def saveAs(self):
        fd = QtGui.QFileDialog(self)
        fileName = unicode(fd.getSaveFileName())
        if not fileName:
            return

        self.textBrowser.saveAs(fileName)



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    QtCore.qsrand(QtCore.QTime(0,0,0).secsTo(QtCore.QTime.currentTime()))

    window = Window()

    window.show()

    sys.exit(app.exec_())
