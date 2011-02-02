""" Lector: scannerthread.py

    Copyright (C) 2011 Davide Setti

    This program is released under the GNU GPLv2
"""

## PyQt
from PyQt4.QtCore import QThread, SIGNAL, QProcess
## SANE
try:
    import sane
except ImportError:
    print "SANE not found!"

from utils import settings

class ScanimageProcess(QProcess):
    def __init__(self, mode, resolution, size):
        super(QProcess, self).__init__()

        self.start("scanimage", ('--format', 'tiff',
                                 '--mode', mode,
                                 '--resolution', str(resolution),
                                 '-x', str(size[0]),
                                 '-y', str(size[1])
                                 )
                   )


class ScannerThread(QThread):
    def __init__(self, parent=None, selectedScanner=None):
        QThread.__init__(self, parent)
        self.selectedScanner = selectedScanner
        self.im = None

    def run(self):
        ## geometry
        #tl_x = 0.0
        #tl_y = 0.0
        br_x = settings.get('scanner:width')
        br_y = settings.get('scanner:height')

        resolution = settings.get('scanner:resolution')
        mode = settings.get('scanner:mode')

        self.process = ScanimageProcess(mode, resolution, (br_x, br_y))
        self.process.connect(self.process, SIGNAL("finished(int)"), self.scanned)

    def scanned(self, exit_code):
        from StringIO import StringIO
        from PIL import Image

        if exit_code:
            print 'ERROR!'
            return #TODO: notify an ERROR!!
        out = self.process.readAllStandardOutput()
        self.im = Image.open(StringIO(out))
        self.emit(SIGNAL("scannedImage()")
