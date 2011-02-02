""" Lector: scannerthread.py

    Copyright (C) 2011 Davide Setti

    This program is released under the GNU GPLv2
"""

## PyQt
from PyQt4.QtCore import QThread, SIGNAL
## SANE
try:
    import sane
except ImportError:
    print "SANE not found!"

from utils import settings

class ScannerThread(QThread):
    def __init__(self, parent=None, selectedScanner=None):
        QThread.__init__(self, parent)
        self.selectedScanner = selectedScanner
        self.im = None

    def run(self):
        s = sane.open(self.selectedScanner)

        ## TODO: make it as option - grayscale is better for OCR
        # print s.get_options()
        s.mode = 'color'

        ## geometry
        try:
            s.tl_x = 0.0
            s.tl_y = 0.0
            s.br_x = settings.get('scanner:width')
            s.br_y = settings.get('scanner:height')
        except AttributeError:
            print "WARNING: Can't set scan geometry"

        s.resolution = settings.get('scanner:resolution')

        #print 'Device parameters:', s.get_parameters()

        # Initialize the scan
        s.start()

        # Get an Image object
        self.im = s.snap()
        self.emit(SIGNAL("scannedImage()"))
