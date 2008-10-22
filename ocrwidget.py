#!/usr/bin/env python

""" Lector: ocrwidget.py

    Copyright (C) 2008 Davide Setti

    This program is released under the GNU GPLv2
""" 

import sys
import Image
#import ImageQt
import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication as qa
from ocrarea import OcrArea
from qocrscene import QOcrScene
#import sys
#sys.path.append('/usr/lib/ooo-2.0/program')
#import uno


class QOcrWidget(QtGui.QGraphicsView):
    def __init__(self, lang, areaType, statusBar):
        QtGui.QGraphicsView.__init__(self)

        self.ocrscene = QOcrScene(self, lang, areaType)
        self.setScene(self.ocrscene)

        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        self.setMinimumSize(200, 200)
        
        self.language = lang
        self.statusBar = statusBar
        self.areaType = areaType
        
        self.first = True
        self.bMovingArea = False
        self.setCursor(QtCore.Qt.CrossCursor)
        self.isModified = False
        

    def drawBackground(self, painter, rect):
        ## TODO: set the background to gray
        #painter.setBackgroundMode(QtCore.Qt.OpaqueMode)
        
        #brushBg = painter.background()
        #brushBg.setColor(QtCore.Qt.darkGreen)
        #painter.setBackground(brushBg)
        
        if hasattr(self, 'ocrImage') and self.ocrImage:
            sceneRect = self.sceneRect()
            painter.drawImage(sceneRect, self.ocrImage)
            #self.statusBar.showMessage(self.tr("Disegno bag"))


    def mouseMoveEvent(self, event):
        sp = self.mapToScene(event.pos())

        ret = self.scene().areaAt(sp)

        edge = ret % 100
        print edge
        #self.setCursor(QtCore.Qt.SizeVerCursor)

        QtGui.QGraphicsView.mouseMoveEvent(self,event)


    def mouseReleaseEvent(self, event):
        self.bMovingArea = False
        if self.itemAt(event.pos()):
            pass
        else:
            if event.button() == QtCore.Qt.LeftButton:
                if self.first == True:
                    self.pos1 = self.mapToScene(event.pos())
                    self.first = False
                else:
                    pos2 = self.mapToScene(event.pos())
                    self.first = True
                    diff = pos2 - self.pos1

                    ## use correct size and pos, also if the clicked points
                    ## are in a strange order
                    size = QtCore.QSizeF(abs(diff.x()), abs(diff.y()))

                    pos = QtCore.QPointF()
                    pos.setX(min(self.pos1.x(), pos2.x()))
                    pos.setY(min(self.pos1.y(), pos2.y()))

                    self.scene().createArea(pos, size, self.areaType, self.areaBorder,
                            self.areaTextSize)

        QtGui.QGraphicsView.mouseReleaseEvent(self,event)


    def cambiaImmagine(self):
        #delete old OcrArea
        for item in self.scene().items():
            self.scene().removeItem(item)
        self.scene().areas = []
        
        #open image
        self.im = Image.open(self.filename)

        #set scene size and view scale
        self.setSceneSize()

        vw = float(self.width())
        vh = float(self.height())
        iw = float(self.im.size[0])
        ih = float(self.im.size[1])
        ratio = min (vw/iw, vh/ih)

        self.setMatrix(QtGui.QMatrix(.95*ratio, 0., 0., .95*ratio, 0., 0.))

        OcrArea.resizeBorder = 5 / ratio
        self.areaBorder = 2 / ratio
        self.areaTextSize = 10 / ratio

        #show image
        self.generateQtImage()
        self.resetCachedContent()
        self.isModified = False


    def rotateRight(self):
        self.im = self.im.rotate(-90)

        self.setSceneSize()
        self.generateQtImage()
        self.resetCachedContent()
        
        
    def rotateLeft(self):
        self.im = self.im.rotate(90)

        self.setSceneSize()
        self.generateQtImage()
        self.resetCachedContent()
        

    def rotateFull(self):
        self.im = self.im.rotate(180)

        self.setSceneSize()
        self.generateQtImage()
        self.resetCachedContent()


    def generateQtImage(self):
        s = self.im.convert("RGB").tostring("jpeg","RGB")

        self.ocrImage = QtGui.QImage()
        self.ocrImage.loadFromData(QtCore.QByteArray(s))

        #print "%d %d %d" % (self.ocrImage.width(), self.ocrImage.height(), self.ocrImage.depth())
        #self.ocrImage = ImageQt.ImageQt(self.im.convert("RGB"))
        #print "%d %d %d" % (self.ocrImage.width(), self.ocrImage.height(), self.ocrImage.depth())


    def setSceneSize(self):
        iw = float(self.im.size[0])
        ih = float(self.im.size[1])
        self.scene().setSceneRect(0, 0, int(iw), int(ih))


    def zoomIn(self):
        self.scale(1.25, 1.25)
        OcrArea.resizeBorder *= 0.8
        self.areaBorder *= 0.8
        self.areaTextSize *= 0.8

        self.scene().updateAreas(self.areaBorder, self.areaTextSize)
                
        self.resetCachedContent()
        self.repaint()


    def zoomOut(self):
        self.scale(0.8, 0.8)
        OcrArea.resizeBorder *= 1.25
        self.areaBorder *= 1.25
        self.areaTextSize *= 1.25

        self.scene().updateAreas(self.areaBorder, self.areaTextSize)

        self.resetCachedContent()
        self.repaint()


    def doOcr(self):
        import codecs
        aItems = self.scene().areas
        numItems = len(aItems)

        self.textBrowser.clear()

        progress = QtGui.QProgressDialog("Sto leggendo le immagini...", "Annulla", 0, numItems)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.forceShow()

        for i, item in enumerate(aItems):
            progress.setValue(i)
            rect = item.rect()
            pos = item.scenePos()
            
            box = (int(pos.x()),int(pos.y()),int(rect.width()+pos.x()),int(rect.height()+pos.y()))
            filename = "/tmp/out.%d.tif" % i

            region = self.im.crop(box)
            
            if item.type == 1:
                region.save(filename)

                command = "tesseract %s /tmp/out.%d -l %s" % (filename, i, self.language)
                os.popen(command)
            
                s = codecs.open("/tmp/out.%d.txt"% (i, ) ,'r','utf-8').read()
                self.textBrowser.append(s)
            else:
                region = region.resize((region.size[0]/4,region.size[1]/4))
                region.save(filename)

                s = "<img src='%s'>" % filename
                self.textBrowser.append(s)

            if (progress.wasCanceled()):
                break;

        progress.setValue(numItems)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            item = self.scene().focusItem()
            self.scene().removeArea(item)
        elif event.key() == QtCore.Qt.Key_Escape:
            self.first = True

        QtGui.QGraphicsView.keyReleaseEvent(self, event)

       
