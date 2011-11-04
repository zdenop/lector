#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Lector: spellchecker.py
    Copyright (C) 2009, John Schember
    
    Modified for Lector by Zdenko Podobný
    This code is released under MIT licence
"""

import re

from PyQt4.Qt import Qt,  QAction, QEvent, QMenu, QMouseEvent
from PyQt4.Qt import QSyntaxHighlighter, QTextCharFormat, QTextCursor
from PyQt4.QtCore import pyqtSignal
 
class Highlighter(QSyntaxHighlighter):
 
    WORDS = u'(?iu)[\w\']+'
 
    def __init__(self, *args):
        QSyntaxHighlighter.__init__(self, *args)
 
        self.dict = None
 
    def setDict(self, dict):
        self.dict = dict
 
    def highlightBlock(self, text):
        if not self.dict:
            return
 
        text = unicode(text)
 
        format = QTextCharFormat()
        format.setUnderlineColor(Qt.red)
        format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
 
        for word_object in re.finditer(self.WORDS, text):
            if not self.dict.check(word_object.group()):
                self.setFormat(word_object.start(),
                    word_object.end() - word_object.start(), format)
 
 
class SpellAction(QAction):
    '''
    A special QAction that returns the text in a signal.
    '''
 
    correct = pyqtSignal(unicode)
 
    def __init__(self, *args):
        QAction.__init__(self, *args)
 
        self.triggered.connect(lambda x: self.correct.emit(
            unicode(self.text())))
