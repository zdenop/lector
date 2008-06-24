#!/usr/bin/env python

""" Lector: ocrwidget.py

    Copyright (C) 2008 Davide Setti

    This program is released under the GNU GPLv2
""" 

#import sys
import Image
#import ImageQt
#import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication as qa
from ocrarea import OcrArea
#import sys
#sys.path.append('/usr/lib/ooo-2.0/program')
#import uno

class QOcrScene(QtGui.QGraphicsScene):
    def __init__(self, parent, lang, areaType):
        QtGui.QGraphicsScene.__init__(self)

        self.language = lang
        self.areaType = areaType
        
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


    def loadImage(self, filename):
        #delete old OcrArea
        for item in self.items():
            self.removeItem(item)
        self.areas = []
        
        #open image
        self.im = Image.open(filename)

        #set scene size and view scale
        self.setSceneSize()
        
        self.createQtImage()


    def setSceneSize(self):
        iw = float(self.im.size[0])
        ih = float(self.im.size[1])
        self.setSceneRect(0, 0, int(iw), int(ih))


    def createQtImage(self):
        s = self.im.convert("RGB").tostring("jpeg","RGB")

        self.ocrImage = QtGui.QImage()
        self.ocrImage.loadFromData(QtCore.QByteArray(s))

        #print "%d %d %d" % (self.ocrImage.width(), self.ocrImage.height(), self.ocrImage.depth())
        #self.ocrImage = ImageQt.ImageQt(self.im.convert("RGB"))
        #print "%d %d %d" % (self.ocrImage.width(), self.ocrImage.height(), self.ocrImage.depth())


    def rotate(self, angle):
        self.im = self.im.rotate(angle)
        
        self.setSceneSize()
        self.createQtImage()
