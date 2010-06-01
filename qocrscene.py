#!/usr/bin/env python

""" Lector: qocrscene.py

    Copyright (C) 2008 Davide Setti

    This program is released under the GNU GPLv2
""" 

from PyQt4 import QtCore, QtGui
from ocrarea import OcrArea


class QOcrScene(QtGui.QGraphicsScene):
    def __init__(self, parent, lang, areaType):
        QtGui.QGraphicsScene.__init__(self)

        self.language = lang
        self.areaType = areaType
        
        self.first = True
        
        self.areas = []


    def createArea(self, pos, size, type_, areaBorder, areaTextSize):
        item = OcrArea(pos, size, type_, None, self, areaBorder,
                len(self.areas) + 1, areaTextSize)

        # grabbing the signal isClicked() and connecting the slot getType when
        # an area is selected
        QtCore.QObject.connect(item.newEvent, QtCore.SIGNAL("isClicked()"),
                               self.getType)

        self.areas.append(item)
        self.isModified = True

        return item

    def removeArea(self, item):
        if item:
            idx = self.areas.index(item)

            self.areas.remove(item)
            self.removeItem(item)
            
            for i, item in enumerate(self.areas[idx:]):
                item.setIndex(i+idx-1)


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
        for i in range(len(self.areas)):
            item = self.areas[i]
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

            if (dyt < OcrArea.resizeBorder):
                edge += 1
            if (dyb < OcrArea.resizeBorder):
                edge += 2
            if (dxl < OcrArea.resizeBorder):
                edge += 4
            if (dxr < OcrArea.resizeBorder):
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
            edge = (onArea) * 100

        return edge

    # when selecting a selected area, it's possibile to
    # view its type in the "change area"
    # and to change it (only with the left button)
    def getType(self):
        area = self.sender()

        if (area.type == 1): 
            self.rbtn_areato_text.setChecked(True)
        elif (area.type == 2): 
            self.rbtn_areato_image.setChecked(True)


    def generateQtImage(self):
        from utils import pilImage2Qt

        self.ocrImage = pilImage2Qt(self.im)
    
    def drawBackground(self, painter, _):
        ## TODO: set the background to gray
        #painter.setBackgroundMode(QtCore.Qt.OpaqueMode)
        
        #brushBg = painter.background()
        #brushBg.setColor(QtCore.Qt.darkGreen)
        #painter.setBackground(brushBg)
        
        if not (hasattr(self, 'ocrImage') and self.ocrImage): return

        sceneRect = self.sceneRect()
        painter.drawImage(sceneRect, self.ocrImage)
        #self.statusBar.showMessage(self.tr("Disegno bag"))

    
    def setSize(self):
        iw = float(self.im.size[0])
        ih = float(self.im.size[1])
        self.setSceneRect(0, 0, int(iw), int(ih))

