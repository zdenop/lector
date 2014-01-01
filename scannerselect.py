#!/usr/bin/env python

""" Lector: scannerselect.py

    Copyright (C) 2008-2011 Davide Setti

    This program is released under the GNU GPLv2
""" 

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import SIGNAL

from ui.ui_scanner import Ui_Scanner
import sane
from utils import settings


class ScannerSelect(QDialog):
    def __init__(self, sane_list, parent = None):
        QDialog.__init__(self, parent)

        self.ui = Ui_Scanner()
        self.ui.setupUi(self)

        self.sane_list = sane_list

        self.ui.combScanner.addItems([scanner[2] for scanner in sane_list])
        sane_devices = [scanner[0] for scanner in sane_list]

        scanner_setting = settings.get('scanner:device')
        #TODO: also load color mode, resolution and size
        try:
            self.ui.combScanner.setCurrentIndex(
                    sane_devices.index(scanner_setting)
            )
        except ValueError:
            pass
        self.updateForm()
        self.connect(self.ui.combScanner, SIGNAL("currentIndexChanged(int)"),
                     self.updateForm)

    def updateForm(self):
        selectedScanner = self.sane_list[self.ui.combScanner.currentIndex()][0]
        saneScanner = sane.open(selectedScanner)

        #this is a list with a lot of info
        options = saneScanner.get_options()
        saneScanner.close()

        #extract just the info we want and put them in a dict
        dOptions = dict([(opt[1], opt[-1]) for opt in options])
        #print '\n'.join(["%s: %s" % (k, str(v)) for k, v in sorted(dOptions.items())])

        #set max and min, if available
        try:
            self.ui.sbHeight.setMaximum(int(dOptions['br-y'][1]))
            self.ui.sbWidth.setMaximum(int(dOptions['br-x'][1]))
        except KeyError:
            ##TODO: if not available (a webcam?) do not use them in scanimage!
            pass

        #set resolution
        try:
            minimum = min(dOptions['resolution'])
            maximum = max(dOptions['resolution'])
        except KeyError:
            pass
        else:
            value = max(minimum, min(300, maximum))
            self.ui.sbResolution.setMaximum(maximum)
            self.ui.sbResolution.setMinimum(minimum)
            self.ui.sbResolution.setValue(value)

        #set color mode
        try:
            modes = dOptions['mode']
        except KeyError:
            pass
        else:
            combo = self.ui.combColor
            combo.clear()
            combo.addItems(modes)

    def accept(self):
        settings.set('scanner:height', self.ui.sbHeight.value())
        settings.set('scanner:width', self.ui.sbWidth.value())
        settings.set('scanner:resolution', self.ui.sbResolution.value())
        settings.set('scanner:mode',
                     self.ui.combColor.currentText())
        settings.set('scanner:device',
                     self.sane_list[self.ui.combScanner.currentIndex()][0])

        QDialog.accept(self)

