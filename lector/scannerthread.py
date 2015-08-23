#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Lector: scannerthread.py

    Copyright (C) 2011-2014 Davide Setti, Zdenko Podobný

    This program is released under the GNU GPLv2
"""
#pylint: disable-msg=C0103

## PyQt
from PyQt4.QtCore import Qt, QThread, QProcess, pyqtSignal
from PyQt5.QtWidgets import QProgressDialog

from utils import settings

class ScanimageProcess(QProcess):
    """ Class fro showing progress dialog of scanning
    """
    def __init__(self, device, mode, resolution, size):
        super(ScanimageProcess, self).__init__()

        self.start("scanimage", ('-d', device,
                                 '-p', '--format=tiff',
                                 '--mode', mode,
                                 '--resolution', str(resolution),
                                 '-x', str(size[0]),
                                 '-y', str(size[1])
                                 )
                   )


def stripProgress(line):
    """
    >>> stripProgress('Progress: 100.0%\r')
    100.0
    >>> stripProgress('Progress: 10.5%\r')
    10.5
    >>> stripProgress('Progress: 0.8%\rProgress: 1.6%\r')
    1.6000000000000001
    """
    return float(line.split('\r')[-2].split(':')[1].strip(' %'))


class ScannerThread(QThread):
    # keep if the image has been loaded
    loaded = False
    scannedImage = pyqtSignal()

    def __init__(self, parent=None, selectedScanner=None):
        QThread.__init__(self, parent)
        self.im = None
        self.device = selectedScanner
        self.process = None
        self.progressDialog = None

    def run(self):
        ## geometry
        #tl_x = 0.0
        #tl_y = 0.0
        br_x = settings.get('scanner:width')
        br_y = settings.get('scanner:height')

        resolution = settings.get('scanner:resolution')
        mode = settings.get('scanner:mode')

        self.process = ScanimageProcess(self.device, mode, resolution,
                                        (br_x, br_y))
        # QObject.connect(self.process, SIGNAL("finished(int)"), self.scanned)
        self.process.finished.connect(self.scanned(int))
        self.process.readyReadStandardError.connect(self.progress)

        #TODO: manage Abort button
        progress = QProgressDialog(
            self.tr("Progress"),
            self.tr("Abort"), 0, 100)
        progress.setWindowTitle(self.tr("Scanning..."))
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.setAutoClose(True)
        progress.setAutoReset(True)
        progress.forceShow()

        self.progressDialog = progress
        self.loaded = False

    def scanned(self, exit_code=0):
        if self.loaded:
            return
        self.loaded = True

        from StringIO import StringIO
        from PIL import Image

        if exit_code:
            print('ERROR!')
            return #TODO: notify an ERROR!!
        out = self.process.readAllStandardOutput()

        self.im = Image.open(StringIO(out))
        self.scannedImage.emit()

    def progress(self):
        line = str(self.process.readAllStandardError())
        progress = stripProgress(line)
        self.progressDialog.setValue(int(progress))

        #TODO: add a setting to enable/disable this ("fast scanning")
        if progress == 100.:
            self.process.readyReadStandardOutput.connect(self.scanned)
