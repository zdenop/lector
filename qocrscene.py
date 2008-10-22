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
        for item in self.areas:
            r = item.rect()

            #diffs between the cursor and item's edges
            dyt = abs(item.y() - pos.y())
            dyb = abs(item.y() + r.height() - pos.y())
            dxl = abs(item.x() - pos.x())
            dxr = abs(item.x() + r.width() - pos.x())

            edge = 0

            if (dyt < OcrArea.resizeBorder):
                edge += 1
                print 'top'
            if (dyb < OcrArea.resizeBorder):
                edge += 2
                print 'bottom'
            if (dxl < OcrArea.resizeBorder):
                edge += 4
                print 'left'
            if (dxr < OcrArea.resizeBorder):
                edge += 8
                print 'right'
            
            if edge: break

        return edge


