#!/usr/bin/env python
# vim: set foldlevel=1:

""" Lector: ocrarea.py

    Copyright (C) 2008 Davide Setti

    This program is released under the GNU GPLv2
""" 

import sys
import Image
import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication as qa
from PyQt4.QtCore import pyqtSignature


class OcrArea(QtGui.QGraphicsRectItem):
    
    ## static data
    resizeborder = .0
    
    def __init__(self, pos, size, type, parent = None, scene = None,
                 areaBorder = 2, index = 0, textSize = 50):
        QtGui.QGraphicsRectItem.__init__(self, 0, 0, size.width(),
                                         size.height(), parent, scene)
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

        pen = QtGui.QPen(self.color, areaBorder, QtCore.Qt.SolidLine,
                         QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self.setPen(pen)
        self.setAcceptsHoverEvents(True)

        # self.text.setFlag(QtGui.QGraphicsItem.ItemIgnoresTransformations)
        # needed for the emission of a signal
        self.newEvent = QtCore.QObject()

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

        ## verification of the type of the selection and
        ## setting a check box near the type that is in use
        textAction.setCheckable(True);
        graphicsAction.setCheckable(True);

        if self.type == 1:
            textAction.setChecked(True)
        elif self.type == 2:
            graphicsAction.setChecked(True)

        selectedAction = menu.exec_(event.screenPos())

        if selectedAction == removeAction:
            self.scene().removeArea(self)
        elif selectedAction == textAction:
            self.type = 1
        elif selectedAction == graphicsAction:
            self.type = 2

    # clicking the change box type events
    # from image type to text
    # or from text type to image
    @pyqtSignature('')
    def on_rbtn_areato_text_clicked(self):
        print self.type
        if (self.type == 2):
            self.type = 1
        print self.type
    
    @pyqtSignature('')
    def on_rbtn_areato_image_clicked(self):
        area = self.type
        if (self.type == 1):
            self.type = 2


    # when the area is selected the signal "isClicked()"
    # is arrized
    def mousePressEvent(self, event):
        self.newEvent.emit(QtCore.SIGNAL("siClicked()"))
        QtGui.QGraphicsRectItem.mousePressEvent(self,event)
 
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


