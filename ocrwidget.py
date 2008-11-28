#!/usr/bin/env python

""" Lector: ocrwidget.py

    Copyright (C) 2008 Davide Setti

    This program is released under the GNU GPLv2
""" 

import sys
import Image
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
        
        self.setCursor(QtCore.Qt.CrossCursor)
        self.scene().isModified = False
        self.bResizing = False
        

    def mouseMoveEvent(self, event):
        sp = self.mapToScene(event.pos())

        if self.bResizing: #if we're resizing an area
            item = self.resizingArea
            r = item.rect()
            pos = item.pos()
            
            newWidth = r.width()
            newHeight = r.height()
            newX, newY = pos.x(), pos.y()

            if self.resizingEdge & 1: #bit mask: top is moving
                #max ensures that y >= 0
                newY = max(0, self.resizingAreaPos.y() + sp.y() - self.resizingStartingPos.y())
                newHeight = self.resizingAreaRect.height() + self.resizingAreaPos.y() - newY
                
            elif self.resizingEdge & 2: #bit mask: bottom is moving
                newHeight = self.resizingAreaRect.height() + sp.y() - self.resizingStartingPos.y()
                
                #force area to be inside the scene
                if newY + newHeight > self.scene().height():
                    newHeight = self.scene().height() - newY

            if self.resizingEdge & 4: #bit mask: right is moving
                newX = max(0, self.resizingAreaPos.x() + sp.x() - self.resizingStartingPos.x())
                newWidth = self.resizingAreaRect.width() + self.resizingAreaPos.x() - newX
            elif self.resizingEdge & 8: #bit mask: right is moving
                newWidth = self.resizingAreaRect.width() + sp.x() - self.resizingStartingPos.x() 
                
                #force area to be inside the scene
                if newX + newWidth > self.scene().width():
                    newWidth = self.scene().width() - newX
            
            #check that height >= OcrArea.resizeBorder
            if newHeight < 2*OcrArea.resizeBorder:
                newHeight = r.height()
                newY = pos.y()
            #check that width >= OcrArea.resizeBorder
            if newWidth < 2*OcrArea.resizeBorder:
                newWidth = r.width()
                newX = pos.x()

            item.setRect(0,0, newWidth, newHeight)
            item.setPos(newX, newY)
            
        else: # if not resizing
            ret = self.scene().areaAt(sp)

            edge = ret % 100
            iArea = ret / 100
            cursors = {0:QtCore.Qt.SizeAllCursor,
                1: QtCore.Qt.SizeVerCursor,
                2: QtCore.Qt.SizeVerCursor,
                4: QtCore.Qt.SizeHorCursor,
                5: QtCore.Qt.SizeFDiagCursor,
                6: QtCore.Qt.SizeBDiagCursor,
                8: QtCore.Qt.SizeHorCursor,
                9: QtCore.Qt.SizeBDiagCursor,
                10: QtCore.Qt.SizeFDiagCursor}

            if iArea:
                self.setCursor(cursors[edge])
            else: # mouse not over an area
                self.setCursor(QtCore.Qt.CrossCursor)

        QtGui.QGraphicsView.mouseMoveEvent(self,event)


    def mousePressEvent(self, event):
        sp = self.mapToScene(event.pos())

        ret = self.scene().areaAt(sp)

        edge = ret % 100
        iArea = ret / 100 - 1
       
        if edge:
            self.bResizing = True
            self.resizingEdge = edge
            self.resizingArea = self.scene().areas[iArea]
            self.resizingStartingPos = sp
            self.resizingAreaRect = self.resizingArea.rect()
            self.resizingAreaPos = self.resizingArea.pos()
            self.resizingArea.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        elif iArea == -1: ##create new area
            size = QtCore.QSizeF(0, 0)
            newArea = self.scene().createArea(sp,
                size, self.areaType, self.areaBorder,
                self.areaTextSize)
            
            self.bResizing = True
            self.resizingEdge = 10
            self.resizingArea = newArea
            self.resizingStartingPos = sp
            self.resizingAreaRect = self.resizingArea.rect()
            self.resizingAreaPos = self.resizingArea.pos()
            self.resizingArea.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)

        QtGui.QGraphicsView.mousePressEvent(self,event)


    def mouseReleaseEvent(self, event):
        if self.bResizing: ## stop resizing
            self.bResizing = False
            r = self.resizingArea.rect()

            ## set min size
            self.resizingArea.setRect(0,0,max(r.width(),
                2*OcrArea.resizeBorder), max(r.height(),
                2*OcrArea.resizeBorder))
            self.resizingArea.setFlag(QtGui.QGraphicsItem.ItemIsMovable,
                True)

        QtGui.QGraphicsView.mouseReleaseEvent(self,event)


    def cambiaImmagine(self):
        #delete old OcrArea
        for item in self.scene().items():
            self.scene().removeItem(item)
        self.scene().areas = []
        
        #open image
        self.scene().im = Image.open(self.filename)

        self.prepareDimensions()


    def prepareDimensions(self):
        #set scene size and view scale
        self.scene().setSize()

        vw = float(self.width())
        vh = float(self.height())
        iw = float(self.scene().im.size[0])
        ih = float(self.scene().im.size[1])
        ratio = min (vw/iw, vh/ih)

        self.setMatrix(QtGui.QMatrix(.95*ratio, 0., 0., .95*ratio, 0., 0.))

        OcrArea.resizeBorder = 5 / ratio
        self.areaBorder = 2 / ratio
        self.areaTextSize = 10 / ratio

        #show image
        self.scene().generateQtImage()
        self.resetCachedContent()
        self.scene().isModified = False


    def rotateRight(self):
        self.scene().im = self.scene().im.rotate(-90)

        self.scene().setSize()
        self.scene().generateQtImage()
        self.resetCachedContent()
        
        
    def rotateLeft(self):
        self.scene().im = self.scene().im.rotate(90)

        self.scene().setSize()
        self.scene().generateQtImage()
        self.resetCachedContent()
        

    def rotateFull(self):
        self.scene().im = self.scene().im.rotate(180)

        self.scene().setSize()
        self.scene().generateQtImage()
        self.resetCachedContent()


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

            region = self.scene().im.crop(box)
            
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
        #elif event.key() == QtCore.Qt.Key_Escape:
        #    self.first = True

        QtGui.QGraphicsView.keyReleaseEvent(self, event)

       
