#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Lector: ocrwidget.py

    Copyright (C) 2011 Davide Setti

    This program is released under the GNU GPLv2
"""
#pylint: disable-msg=C0103

import os
import math
import glob
from PIL import Image

from PyQt5.QtGui import QPainter, QTransform, QIcon
from PyQt5.QtCore import Qt, QSizeF, QRectF
from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem, QProgressDialog

from ocrarea import OcrArea
from ocrscene import OcrScene
from utils import settings

class QOcrWidget(QGraphicsView):
    def __init__(self, lang, areaType, statusBar):
        QGraphicsView.__init__(self)

        self.ocrscene = OcrScene(self, lang, areaType)
        self.setScene(self.ocrscene)

        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        self.setMinimumSize(200, 200)

        self.language = lang
        self.statusBar = statusBar
        self.areaType = areaType

        self.resizingArea = None
        self.resizingAreaPos = None
        self.resizingAreaRect = None
        self.resizingEdge = None
        self.resizingStartingPos = None
        self.areaBorder = float()
        self.areaTextSize = float()

        self.setCursor(Qt.CrossCursor)
        self.scene().isModified = False
        self.bResizing = False
        Image.init()

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
                newY = max(0, self.resizingAreaPos.y() + sp.y() - \
                            self.resizingStartingPos.y())
                newHeight = self.resizingAreaRect.height() + \
                            self.resizingAreaPos.y() - newY

            elif self.resizingEdge & 2: #bit mask: bottom is moving
                newHeight = self.resizingAreaRect.height() + sp.y() - \
                            self.resizingStartingPos.y()

                #force area to be inside the scene
                if newY + newHeight > self.scene().height():
                    newHeight = self.scene().height() - newY

            if self.resizingEdge & 4: #bit mask: right is moving
                newX = max(0, self.resizingAreaPos.x() + sp.x() - \
                            self.resizingStartingPos.x())
                newWidth = self.resizingAreaRect.width() + \
                            self.resizingAreaPos.x() - newX
            elif self.resizingEdge & 8: #bit mask: right is moving
                newWidth = self.resizingAreaRect.width() + sp.x() - \
                            self.resizingStartingPos.x()

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

            item.setRect(0, 0, newWidth, newHeight)
            item.setPos(newX, newY)

        else: # if not resizing
            # grabbing the position of the widget
            sp = self.mapToScene(event.pos())
            ret = self.scene().areaAt(sp)

            edge = ret % 100
            iArea = ret / 100
            cursors = {0:Qt.SizeAllCursor,
                1: Qt.SizeVerCursor,
                2: Qt.SizeVerCursor,
                4: Qt.SizeHorCursor,
                5: Qt.SizeFDiagCursor,
                6: Qt.SizeBDiagCursor,
                8: Qt.SizeHorCursor,
                9: Qt.SizeBDiagCursor,
                10: Qt.SizeFDiagCursor}

            if iArea:
                self.setCursor(cursors[edge])
            else: # mouse not over an area
                self.setCursor(Qt.CrossCursor)

        QGraphicsView.mouseMoveEvent(self, event)


    def mousePressEvent(self, event):
        # grabbing the position of the widget
        sp = self.mapToScene(event.pos())
        ret = self.scene().areaAt(sp)

        edge = ret % 100
        iArea = ret / 100 - 1

        # resizing/moving the area if it exists
        if edge:
            self.bResizing = True
            self.resizingEdge = edge
            self.resizingArea = self.scene().areas[iArea]
            self.resizingStartingPos = sp
            self.resizingAreaRect = self.resizingArea.rect()
            self.resizingAreaPos = self.resizingArea.pos()
            self.resizingArea.setFlag(QGraphicsItem.ItemIsMovable, False)
        # creation of a new area if there is an image
        elif iArea == -1 and self.filename:
            size = QSizeF(0, 0)
            newArea = self.scene().createArea(sp,
                size, self.areaType, self.areaBorder,
                self.areaTextSize)

            self.bResizing = True
            self.resizingEdge = 10
            self.resizingArea = newArea
            self.resizingStartingPos = sp
            self.resizingAreaRect = self.resizingArea.rect()
            self.resizingAreaPos = self.resizingArea.pos()
            self.resizingArea.setFlag(QGraphicsItem.ItemIsMovable, False)

        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.bResizing: ## stop resizing
            self.bResizing = False
            r = self.resizingArea.rect()

            ## set min size
            self.resizingArea.setRect(0, 0, max(r.width(),
                2*OcrArea.resizeBorder), max(r.height(),
                2*OcrArea.resizeBorder))
            self.resizingArea.setFlag(QGraphicsItem.ItemIsMovable,
                True)

        QGraphicsView.mouseReleaseEvent(self, event)


    def wheelEvent(self, event):
        '''Zoom In/Out with CTRL + mouse wheel'''
        if event.modifiers() == Qt.ControlModifier:
            self.scaleView(math.pow(2.0, -event.angleDelta().y() / 240.0))
        else:
            return QGraphicsView.wheelEvent(self, event)

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(scaleFactor, scaleFactor). \
            mapRect(QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)

    def changeImage(self):
        #delete old OcrArea
        for item in self.scene().items():
            self.scene().removeItem(item)
        self.scene().areas = []

        #open image
        self.scene().im = Image.open(self.filename)
        self.prepareDimensions()


    def prepareDimensions(self):
        #set scene size and view scale
        scene = self.scene()
        scene.setSize()

        vw = float(self.width())
        vh = float(self.height())
        iw = float(scene.im.size[0])
        ih = float(scene.im.size[1])
        ratio = min(vw/iw, vh/ih)
        # TODO: check this - there was QMatrix
        # self.setMatrix(QTransform(.95*ratio, 0., 0., .95*ratio, 0., 0.))

        OcrArea.resizeBorder = 5 / ratio
        self.areaBorder = 2 / ratio
        self.areaTextSize = 10 / ratio

        #show image
        scene.generateQtImage()
        self.resetCachedContent()
        scene.isModified = False


    def rotate(self, angle):
        scene = self.scene()
        scene.im = scene.im.rotate(angle)

        scene.setSize()
        scene.generateQtImage()
        self.resetCachedContent()

    def rotateRight(self):
        self.rotate(-90)

    def rotateLeft(self):
        self.rotate(90)

    def rotateFull(self):
        self.rotate(180)

    def zoom(self, factor):
        inv_factor = 1./factor
        self.scale(factor, factor)
        OcrArea.resizeBorder *= inv_factor
        self.areaBorder *= inv_factor
        self.areaTextSize *= inv_factor

        self.scene().updateAreas(self.areaBorder, self.areaTextSize)

        self.resetCachedContent()
        self.repaint()

    def zoomIn(self):
        self.zoom(1.25)

    def zoomOut(self):
        self.zoom(.8)

    def doOcr(self):
        import codecs
        aItems = self.scene().areas
        numItems = len(aItems)

        if settings.get('editor:clear') :
            self.textEditor.clear()

        # clean temp to avoid false imports
        for oldOutPut in glob.glob('/tmp/out.[0-9]*.txt'):
            os.remove(oldOutPut)

        progress = QProgressDialog(self.tr("Processing images..."),
                                         self.tr("Abort"), 0, numItems)
        progress.setWindowTitle(self.tr("Processing images..."))
        progress.setWindowModality(Qt.WindowModal)
        # on MS Windows dialog has no icon
        progress.setWindowIcon(QIcon(":/icons/icons/L.png"))
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.setAutoClose(True)
        progress.setAutoReset(True)
        progress.forceShow()

        tess_exec = settings.get('tesseract-ocr:executable')
        if not tess_exec:
            tess_exec = 'tesseract'

        for i, item in enumerate(aItems):
            if progress.wasCanceled():
                break

            progress.setValue(i)
            rect = item.rect()
            pos = item.scenePos()

            box = (int(pos.x()), int(pos.y()), int(rect.width() + pos.x()), \
                    int(rect.height() + pos.y()))
            # TODO: make random filename if we do not debug lector ;-)
            # TODO: use png if tesseract version is > 3.00
            filename = "/tmp/out.%d.png" % i

            region = self.scene().im.crop(box)

            if item.type == 1:
                # Improve quality of text for tesseract
                # TODO: put it as option for OCR because of longer duration
                nx, ny = rect.width(), rect.height()
                region = region.resize((int(nx*3), int(ny*3)), \
                            Image.BICUBIC).convert('L')
                region.save(filename, dpi=(600, 600))
                # TODO: use html/hocr if tesseract version is > 3.01
                command = tess_exec + " %s /tmp/out.%d -l %s" % (filename, i,
                                                              self.language)
                os.popen(command)

                if os.path.exists("/tmp/out.%d.txt" % i):
                    s = codecs.open("/tmp/out.%d.txt" % \
                        (i, ) , 'r', 'utf-8').read()
                    self.textEditor.append(s)
                    # TODO: delete image & OCR result if we do not debug lector
                else:
                    ## TODO: tesseract failed.
                    ## 1. process/print error message
                    ## 2. mark area as problematic
                    print("Tesseract was unabled to process area!")
                    # this can happend if left side of text is blury
            else:
                region = region.resize((region.size[0]/4, region.size[1]/4))
                region.save(filename)

                s = "<img src='%s'>" % filename
                self.textEditor.append(s)

        progress.setValue(numItems)


    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Delete:
            item = self.scene().focusItem()
            self.scene().removeArea(item)
        #elif event.key() == Qt.Key_Escape:
        #    self.first = True

        QGraphicsView.keyReleaseEvent(self, event)

