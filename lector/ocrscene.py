#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Lector: ocrscene.py

    Copyright (C) 2011-2014 Davide Setti, Zdenko Podobný

    This program is released under the GNU GPLv2
"""
#pylint: disable-msg=C0103

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene

from ocrarea import OcrArea


class OcrScene(QGraphicsScene):
    selectedAreaIdx = None
    changedSelectedAreaType = pyqtSignal()

    def __init__(self, _, lang, areaType):
        QGraphicsScene.__init__(self)

        self.language = lang
        self.areaType = areaType
        self.first = True
        self.areas = []
        self.ocrImage = None
        self.isModified = None

    def createArea(self, pos, size, type_, areaBorder, areaTextSize):
        item = OcrArea(pos, size, type_, None, self, areaBorder,
                len(self.areas) + 1, areaTextSize)

        self.areas.append(item)
        item.newEvent.isClicked.connect(self.changedSelection)
        self.setFocusItem(item)
        self.isModified = True

        return item

    def removeArea(self, item):
        if item is None:
            return

        idx = self.areas.index(item)

        self.areas.remove(item)
        self.removeItem(item)
        self.selectedAreaIdx = None

        for i, item in enumerate(self.areas[idx:]):
            item.setIndex(i+idx-1)

        self.__emitChangedSelection(0)

    def updateAreas(self, areaBorder, areaTextSize):
        def resizeBorderAndText(item):
            # resize border
            pen = item.pen()
            pen.setWidthF(areaBorder)
            item.setPen(pen)
            item.setTextSize(areaTextSize)

        map(resizeBorderAndText, self.areas)


    def areaAt(self, pos):
        edge = 0
        onArea = 0
        for i, item in enumerate(self.areas):
            r = item.rect()

            # this is not very clean... it checks that the mouse is over an
            # area + its resize borders. The only diffs are not enough: they
            # give true also if (i.e) the mouse is horizontally in line with
            # the top border, but far away from the area
            if not ((item.y() + r.height() + OcrArea.resizeBorder > pos.y())
                    and (item.y() - OcrArea.resizeBorder < pos.y()) and (
                        item.x() + r.width() + OcrArea.resizeBorder > pos.x())
                    and (item.x() - OcrArea.resizeBorder < pos.x())):
                continue

            #diffs between the cursor and item's edges
            dyt = abs(item.y() - pos.y())
            dyb = abs(item.y() + r.height() - pos.y())
            dxl = abs(item.x() - pos.x())
            dxr = abs(item.x() + r.width() - pos.x())

            edge = 0

            if dyt < OcrArea.resizeBorder:
                edge += 1
            if dyb < OcrArea.resizeBorder:
                edge += 2
            if dxl < OcrArea.resizeBorder:
                edge += 4
            if dxr < OcrArea.resizeBorder:
                edge += 8

            if not onArea:
                if ((item.y() + r.height() > pos.y()) and (item.y() < pos.y())
                    and (item.x() + r.width() > pos.x()) and (
                        item.x() < pos.x())):
                    onArea = i + 1

            if edge:
                edge += (i+1)*100
                break

        if not edge:
            edge = onArea * 100

        return edge

    def generateQtImage(self):
        from utils import pilImage2Qt

        self.ocrImage = pilImage2Qt(self.im)

    def drawBackground(self, painter, _):
        ## TODO: set the background to gray
        #painter.setBackgroundMode(QtCore.Qt.OpaqueMode)

        #brushBg = painter.background()
        #brushBg.setColor(QtCore.Qt.darkGreen)
        #painter.setBackground(brushBg)

        if not (hasattr(self, 'ocrImage') and self.ocrImage):
            return

        sceneRect = self.sceneRect()
        painter.drawImage(sceneRect, self.ocrImage)
        #self.statusBar.showMessage(self.tr("Disegno bag"))

    def setSize(self):
        iw = float(self.im.size[0])
        ih = float(self.im.size[1])
        self.setSceneRect(0, 0, int(iw), int(ih))

    # when selecting a selected area, it's possibile to
    # view its type in the "change area"
    # and to change it (only with the left button)
    def changedSelection(self):
        area = self.sender().area
        self.selectedAreaIdx = self.areas.index(area)
        self.__emitChangedSelection(area.type)

    def __emitChangedSelection(self, _type):
        self.changedSelectedAreaType.emit(_type)

    def changeSelectedAreaType(self, _type):
        try:
            self.areas[self.selectedAreaIdx].type = _type
        except TypeError:
            pass