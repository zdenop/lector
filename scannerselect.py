#!/usr/bin/env python

""" Lector: scannerselect.py

    Copyright (C) 2011 Davide Setti

    This program is released under the GNU GPLv2
""" 

from PyQt4.QtGui import QDialog, QVBoxLayout, QGroupBox, QRadioButton, \
         QHBoxLayout, QPushButton
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QApplication as qa


class ScannerSelect(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.radio_group = QGroupBox(self)
        layout.addWidget(self.radio_group)

        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout, 0)

        #add the OK and Cancel buttons to the bottom
        btn_layout.addStretch()
        ok = QPushButton()
        ok.setText(qa.tr(self, "OK"))
        btn_layout.addWidget(ok)
        cancel = QPushButton()
        cancel.setText(qa.tr(self, "Cancel"))
        btn_layout.addWidget(cancel)

        self.connect(ok, SIGNAL("clicked()"), self.accept)
        self.connect(cancel, SIGNAL("clicked()"), self.reject)

    def getSelectedIndex(self, title, items, _):
        ## TODO: what's the last argument?
        self.radio_group.setTitle(title)
        
        radio_layout = QVBoxLayout(self.radio_group)
        radios = []
        for item in items:
            radio = QRadioButton(item)
            radios.append(radio)
            radio_layout.addWidget(radio)#, self.radio_group))

        if self.exec_():
            for index, radio in enumerate(radios):
                if radio.isChecked():
                    return index
            
        return -1
            
