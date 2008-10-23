#!/usr/bin/env python

""" Lector: ocrarea.py

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


class QOcrScene(QtGui.QGraphicsScene):
    def __init__(self, parent, lang, areaType):
        QtGui.QGraphicsScene.__init__(self)

        self.language = lang
        self.areaType = areaType
        
        self.first = True
        
        self.areas = []


    def createArea(self, pos, size, type, areaBorder, areaTextSize):
        item = OcrArea(pos, size, type, None, self, areaBorder,
                len(self.areas) + 1, areaTextSize)

        self.areas.append(item)
        self.isModified = True


    def removeArea(self, item):
        if item:
            idx = self.areas.index(item)

            self.areas.remove(item)
            self.removeItem(item)
            for i, item in enumerate(self.areas[idx:]):
                item.setIndex(i+idx+1)


    def updateAreas(self, areaBorder, areaTextSize):    
        for item in self.areas:
            # resize border
            pen = item.pen()
            pen.setWidthF(areaBorder)
            item.setPen(pen)
            item.setTextSize(areaTextSize)


    def areaAt(self, pos):
        edge = 0
        onArea = 0
        for i in range(len(self.areas)):
            item = self.areas[i]
            r = item.rect()

            # this is not very clean... it checks that the mouse is over an area + its resize borders. The only diffs are not enough: they give true also if (i.e) the mouse is horizontally in line with the top border, but far away from the area
            if not ((item.y() + r.height() + OcrArea.resizeBorder > pos.y()) and (item.y() - OcrArea.resizeBorder < pos.y()) and (item.x() + r.width() + OcrArea.resizeBorder > pos.x()) and (item.x() - OcrArea.resizeBorder < pos.x())):
                continue

            #diffs between the cursor and item's edges
            dyt = abs(item.y() - pos.y())
            dyb = abs(item.y() + r.height() - pos.y())
            dxl = abs(item.x() - pos.x())
            dxr = abs(item.x() + r.width() - pos.x())

            edge = 0

            if (dyt < OcrArea.resizeBorder):
                edge += 1
            if (dyb < OcrArea.resizeBorder):
                edge += 2
            if (dxl < OcrArea.resizeBorder):
                edge += 4
            if (dxr < OcrArea.resizeBorder):
                edge += 8
            
            if not onArea:
                if (item.y() + r.height() > pos.y()) and (item.y() < pos.y()) and (item.x() + r.width() > pos.x()) and (item.x() < pos.x()):
                    onArea = i + 1

            if edge:
                edge += (i+1)*100
                break

        if not edge:
            edge = (onArea) * 100

        return edge


