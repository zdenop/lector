#!/usr/bin/env python

""" Lector: ocrarea.py

    Copyright (C) 2008 Davide Setti

    This program is released under the GNU GPLv2
""" 

import sys
import Image
import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication as qa


class OcrArea(QtGui.QGraphicsRectItem):
    
    ## static data
    resizeborder = .0
    
    def __init__(self, pos, size, type, parent = None, scene = None, areaBorder = 2, index = 0, textSize = 50):
        QtGui.QGraphicsRectItem.__init__(self, 0, 0, size.width(), size.height(), parent, scene)
        self.setPos(pos)
        
        #self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable |
            QtGui.QGraphicsItem.ItemIsFocusable |
            QtGui.QGraphicsItem.ItemIsSelectable)
        
        ## set index label
        self.text = QtGui.QGraphicsTextItem("%d" % index, self)
        self.setTextSize(textSize)

        ## TODO: come creare delle costanti per il tipo? (come le costanti nelle Qt) (enum?)
        self.type = type

        pen = QtGui.QPen(self.color, areaBorder, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self.setPen(pen)
        self.setAcceptsHoverEvents(True)
        #self.setCursor(QtCore.Qt.SizeAllCursor)

        # self.text.setFlag(QtGui.QGraphicsItem.ItemIgnoresTransformations)


    #def mousePressEvent(self, event):
    #    self.update()

    #    r = self.rect()
    #    if event.pos().x() > (r.right() - OcrArea.resizeBorder) :
    #        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
    #        self.sEdge = "Right"

    #    elif event.pos().x() < (r.left() + OcrArea.resizeBorder) :
    #        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
    #        self.sEdge = "Left"

    #    elif event.pos().y() < (r.top() + OcrArea.resizeBorder) :
    #        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
    #        self.sEdge = "Top"

    #    elif event.pos().y() > (r.bottom() - OcrArea.resizeBorder) :
    #        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
    #        self.sEdge = "Bottom"

    #    QtGui.QGraphicsItem.mousePressEvent(self, event)


    #def mouseReleaseEvent(self, event):
    #    self.update()
    #    self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
    #    self.sEdge = ''
    #    QtGui.QGraphicsItem.mouseReleaseEvent(self, event)


    def mouseMoveEvent(self, event):
        self.update()

    #    if hasattr(self, 'sEdge') and self.sEdge:
    #        r = self.rect()
    #        scenePos = event.scenePos()

    #        ## TODO: possibile scriverlo in modo piu` semplice tenendo dei punti fissi?
    #        ## del tipo: blocco quel lato, mentre questo lo metto "sotto il cursore" (event.scenePos())
    #        if self.sEdge == 'Top':
    #            diff = self.y() - scenePos.y()
    #            if r.height() - diff > 0:
    #                self.setPos(self.x(), scenePos.y())
    #                self.setRect(0,0,r.width(),r.height() + diff)
    #            else:
    #                self.sEdge = "Bottom"
    #                self.setPos(self.x(), self.y()+r.height())
    #                self.setRect(0,0, r.width(), diff - r.height())

    #        elif self.sEdge == 'Left':
    #            diff = self.x() - scenePos.x()
    #            if r.width() - diff > 0:
    #                self.setPos(scenePos.x(), self.y())
    #                self.setRect(0,0,r.width()+diff,r.height())
    #            else:
    #                self.sEdge = "Right"
    #                self.setPos(self.x()+r.width(), self.y())
    #                self.setRect(0,0, diff - r.width(), r.height())

    #        elif self.sEdge == 'Bottom':
    #            if r.height() > 0:
    #                pos = self.mapFromScene(scenePos)
    #                self.setRect(0,0,r.width(),pos.y())
    #            else:
    #                self.setRect(0,0, r.width(), abs(scenePos.y()-self.y()))
    #                self.setPos(self.x(), scenePos.y())
    #                self.sEdge = "Top"
    #        elif self.sEdge == 'Right':
    #            if r.width() > 0:
    #                pos = self.mapFromScene(scenePos)
    #                self.setRect(0,0,pos.x(),r.height())
    #            else:
    #                self.setRect(0,0, abs(scenePos.x()-self.x()), r.height())
    #                self.setPos(scenePos.x(), self.y())
    #                self.sEdge = "Left"

        QtGui.QGraphicsItem.mouseMoveEvent(self, event)


    #def hoverMoveEvent(self, event):
    #    r = self.rect()
    #    if event.pos().x() > (r.right() - OcrArea.resizeBorder) :
    #        self.setCursor(QtCore.Qt.SizeHorCursor)

    #    elif event.pos().x() < (r.left() + OcrArea.resizeBorder) :
    #        self.setCursor(QtCore.Qt.SizeHorCursor)

    #    elif event.pos().y() < (r.top() + OcrArea.resizeBorder) :
    #        self.setCursor(QtCore.Qt.SizeVerCursor)

    #    elif event.pos().y() > (r.bottom() - OcrArea.resizeBorder) :
    #        self.setCursor(QtCore.Qt.SizeVerCursor)

    #    else:
    #        self.setCursor(QtCore.Qt.SizeAllCursor)


    def setIndex(self, idx):
        self.text.setPlainText("%d" % idx)


    def setTextSize(self, size):
        font = QtGui.QFont()
        font.setPointSizeF(size)
        self.text.setFont(font)


    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        removeAction = menu.addAction(qa.translate('QOcrWidget', "Remove"))
        #Action = menu.addAction(self.scene().tr("Remove"))
        menu.addSeparator()
        textAction = menu.addAction(qa.translate('QOcrWidget', "Text"))
        graphicsAction = menu.addAction(qa.translate('QOcrWidget', "Graphics"))
        selectedAction = menu.exec_(event.screenPos())

        if selectedAction == removeAction:
            self.scene().removeArea(self)
        elif selectedAction == textAction:
            self.type = 1
        elif selectedAction == graphicsAction:
            self.type = 2


    ## type property
    def _setType(self, type):
        self.__type = type
        
        if self.__type == 1:
            self.color = QtCore.Qt.darkGreen
        else: ## TODO: else -> elif ... + else raise exception
            self.color = QtCore.Qt.blue
        
        self.text.setDefaultTextColor(self.color)

        pen = self.pen()
        pen.setColor(self.color)
        self.setPen(pen)

    def _type(self):
        return self.__type

    type = property(fget=_type, fset=_setType)


