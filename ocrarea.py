#!/usr/bin/env python

""" Lector: ocrarea.py

    Copyright (C) 2011 Davide Setti

    This program is released under the GNU GPLv2
""" 

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication as qa


class OcrArea(QtGui.QGraphicsRectItem):
    ## static data
    resizeborder = .0

    def __init__(self, pos, size, type_, parent = None, scene = None,
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

        ## TODO: come creare delle costanti per il tipo?
        ## (come le costanti nelle Qt) (enum?)
        self.type = type_

        pen = QtGui.QPen(self.color, areaBorder, QtCore.Qt.SolidLine,
                         QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self.setPen(pen)
        self.setAcceptsHoverEvents(True)

        # self.text.setFlag(QtGui.QGraphicsItem.ItemIgnoresTransformations)
        # needed for the emission of a signal
        self.newEvent = QtCore.QObject()
        self.newEvent.area = self

    def setIndex(self, idx):
        self.text.setPlainText(str(idx))

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
        textAction.setCheckable(True)
        graphicsAction.setCheckable(True)

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

    # when the area is selected the signal "isClicked()" is raised
    def mousePressEvent(self, event):
        self.newEvent.emit(QtCore.SIGNAL("isClicked()"))
        QtGui.QGraphicsRectItem.mousePressEvent(self, event)

    ## type property
    def _setType(self, type_):
        self.__type = type_

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


