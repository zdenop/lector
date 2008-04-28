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
#import sys
#sys.path.append('/usr/lib/ooo-2.0/program')
#import uno

class QOcrWidget(QtGui.QGraphicsView):
    def __init__(self, lang, areaType, statusBar):
        QtGui.QGraphicsView.__init__(self)

        scene = QtGui.QGraphicsScene(self)
        self.setScene(scene)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        self.setMinimumSize(200, 200)
        
        self.language = lang
        self.statusBar = statusBar
        self.areaType = 1
        
        self.first = True
        self.bMovingArea = False
        self.setCursor(QtCore.Qt.CrossCursor)
        self.isModified = False
        
        self.areas = []


    def drawBackground(self, painter, rect):
        if hasattr(self, 'ocrImage') and self.ocrImage:
            sceneRect = self.sceneRect()
            painter.drawImage(sceneRect, self.ocrImage)
            #self.statusBar.showMessage(self.tr("Disegno bag"))


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

                    size = QtCore.QSizeF(diff.x(), diff.y())
                    rect = QtCore.QRectF(self.pos1, size)

                    item = OcrArea(0, 0, diff.x(), diff.y(), self.areaType, None, self.scene(),
                            self.areaBorder, self.areaResizeBorder, len(self.areas) + 1,
                            self.areaTextSize)
                    item.setPos(self.pos1)

                    self.areas.append(item)

                    self.isModified = True

        QtGui.QGraphicsView.mouseReleaseEvent(self,event)


    def cambiaImmagine(self):
        #delete old OcrArea
        for item in self.scene().items():
            self.scene().removeItem(item)
        
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

        self.areaResizeBorder = 5 / ratio
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
        self.areaResizeBorder *= 0.8
        self.areaBorder *= 0.8
        self.areaTextSize *= 0.8

        for item in self.areas:
            # resize area on which area is resizable
            item.resizeBorder = self.areaResizeBorder
            
            # resize border
            pen = item.pen()
            pen.setWidthF(self.areaBorder)
            item.setPen(pen)
            item.setTextSize(self.areaTextSize)
        
        self.resetCachedContent()
        self.repaint()


    def zoomOut(self):
        self.scale(0.8, 0.8)
        self.areaResizeBorder *= 1.25
        self.areaBorder *= 1.25
        self.areaTextSize *= 1.25

        for item in self.areas:
            # resize area on which area is resizable
            item.resizeBorder = self.areaResizeBorder
            
            # resize border
            pen = item.pen()
            pen.setWidthF(self.areaBorder)
            item.setPen(pen)
            item.setTextSize(self.areaTextSize)
        
        self.resetCachedContent()
        self.repaint()


    def doOcr(self):
        import codecs
        aItems = self.areas
        numItems = len(aItems)

        self.textBrowser.clear()

        #TODO: annulla non utilizzato
        progress = QtGui.QProgressDialog("Sto leggendo le immagini...", "Annulla", 0, numItems)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setMinimumDuration(0)

        i = 0
        for item in aItems:
            progress.setValue(i)
            rect = item.rect()
            pos = item.scenePos()
            
            box = (int(pos.x()),int(pos.y()),int(rect.width()+pos.x()),int(rect.height()+pos.y()))
            filename = "/tmp/out.%d.tif" % i

            region = self.im.crop(box)
            region.save(filename)
            
            if item.type == 1:
                command = "tesseract /tmp/out.tif /tmp/out.%d -l %s" % (i, self.language)
                os.popen(command)
            
                s = codecs.open("/tmp/out.%d.txt"% (i, ) ,'r','utf-8').read()
                self.textBrowser.append(s)
            else:
                s = "<img src='%s'>" % filename
                self.textBrowser.append(s)

            i = i + 1
        
        progress.setValue(numItems)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            item = self.scene().focusItem()
            if item:
                idx = self.areas.index(item)

                self.areas.remove(item)
                self.scene().removeItem(item)
                for i, item in enumerate(self.areas[idx:]):
                    item.setIndex(i+idx+1)
        elif event.key() == QtCore.Qt.Key_Escape:
            self.first = True

        QtGui.QGraphicsView.keyReleaseEvent(self, event)

       


class OcrArea(QtGui.QGraphicsRectItem):
    
    def __init__(self, x, y, w, h, type, parent = None, scene = None, areaBorder = 2, resizeBorder = 5, index = 0, textSize = 50):
        QtGui.QGraphicsRectItem.__init__(self, x, y, w, h, parent, scene)

        #self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)

        ## TODO: come creare delle costanti per il tipo? (come le costanti nelle Qt)
        self.type = type
        if self.type == 1:
            self.color = QtCore.Qt.darkGreen
        else: ## TODO: else -> elif ... + else raise exception
            self.color = QtCore.Qt.blue

        pen = QtGui.QPen(self.color, areaBorder, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self.setPen(pen)
        self.setAcceptsHoverEvents(True)
        self.setCursor(QtCore.Qt.SizeAllCursor)
        self.resizeBorder = resizeBorder

        ## set index label
        self.text = QtGui.QGraphicsTextItem("%d" % index, self)

        self.setTextSize(textSize)
        self.text.setDefaultTextColor(self.color)
        # self.text.setFlag(QtGui.QGraphicsItem.ItemIgnoresTransformations)



    def mousePressEvent(self, event):
        self.update()

        r = self.rect()
        if event.pos().x() > (r.right() - self.resizeBorder) :
            self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
            self.sEdge = "Right"

        elif event.pos().x() < (r.left() + self.resizeBorder) :
            self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
            self.sEdge = "Left"

        elif event.pos().y() < (r.top() + self.resizeBorder) :
            self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
            self.sEdge = "Top"

        elif event.pos().y() > (r.bottom() - self.resizeBorder) :
            self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
            self.sEdge = "Bottom"

        QtGui.QGraphicsItem.mousePressEvent(self, event)


    def mouseReleaseEvent(self, event):
        self.update()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.sEdge = ''
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)


    def mouseMoveEvent(self, event):
        self.update()

        if hasattr(self, 'sEdge') and self.sEdge:
            r = self.rect()

            if self.sEdge == 'Top':
                diff = self.y() - event.scenePos().y()
                self.setPos(self.x(), event.scenePos().y())
                self.setRect(0,0,r.width(),r.height() + diff)
            elif self.sEdge == 'Left':
                diff = self.x() - event.scenePos().x()
                self.setPos(event.scenePos().x(), self.y())
                self.setRect(0,0,r.width()+diff,r.height())
            elif self.sEdge == 'Bottom':
                scenePos = event.scenePos()
                pos = self.mapFromScene(scenePos)
                self.setRect(0,0,r.width(),pos.y())
            elif self.sEdge == 'Right':
                scenePos = event.scenePos()
                pos = self.mapFromScene(scenePos)
                self.setRect(0,0,pos.x(),r.height())

        QtGui.QGraphicsItem.mouseMoveEvent(self, event)


    def hoverMoveEvent(self, event):
        r = self.rect()
        if event.pos().x() > (r.right() - self.resizeBorder) :
            self.setCursor(QtCore.Qt.SizeHorCursor)

        elif event.pos().x() < (r.left() + self.resizeBorder) :
            self.setCursor(QtCore.Qt.SizeHorCursor)

        elif event.pos().y() < (r.top() + self.resizeBorder) :
            self.setCursor(QtCore.Qt.SizeVerCursor)

        elif event.pos().y() > (r.bottom() - self.resizeBorder) :
            self.setCursor(QtCore.Qt.SizeVerCursor)

        else:
            self.setCursor(QtCore.Qt.SizeAllCursor)


    def setIndex(self, idx):
        self.text.setPlainText("%d" % idx)


    def setTextSize(self, size):
        font = QtGui.QFont()
        font.setPointSizeF(size)
        self.text.setFont(font)
