#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Lector utils

    Copyright (C) 2011 Davide Setti, Zdenko Podobný
    Website: http://code.google.com/p/lector

    This program is released under the GNU GPLv2

"""
from PyQt4.QtGui import QImage
from subprocess import Popen, PIPE
from glob import glob
import os


def pilImage2Qt(im):
    if im.mode != 'RGB':
        im = im.convert('RGB')
    s = im.tostring("jpeg", "RGB")

    qtimage = QImage()
    qtimage.loadFromData(s)
    return qtimage

    #from PIL import ImageQt
    #qtimage = ImageQt.ImageQt(im)
    #return qtimage


def extract_tesseract_languages_path(error_message):
    """
    >>> extract_tesseract_languages_path("Unable to load unicharset file /usr/share/tesseract-ocr/tessdata/invalid.unicharset")
    ('/usr/share/tesseract-ocr/tessdata', '.unicharset')
    """
    # problem if there is space in path
    invalid_path = error_message.split()[-1]  
    path, invalid_fn = os.path.split(invalid_path)
    _, extension = os.path.splitext(invalid_fn)
    return path, extension


def get_tesseract_languages():
    """
    make a list of installed language data files
    """

    try:
        poTess = Popen(['tesseract', 'a', 'a', '-l', 'invalid'],
                       shell=False, stdout=PIPE, stderr=PIPE)
        stdout_message, lTess = poTess.communicate()
        tessdata_path, langdata_ext = extract_tesseract_languages_path(lTess)
    except OSError, ex:
        print "ex", ex
        return None

    # env. setting can help to handle path with spaces
    if os.getenv('TESSDATA_PREFIX'):
        tessdata_path = os.path.join(os.getenv('TESSDATA_PREFIX'), "tessdata")

    if not os.path.exists(tessdata_path):
        print "Tesseract data path ('%s') do not exist!" % tessdata_path
        return None
        
    langdata = glob(tessdata_path + os.path.sep + '*' + langdata_ext)
    return [os.path.splitext(os.path.split(uc)[1])[0] for uc in langdata]

def get_spellchecker_languages(directory = None):
    """
    Check if spellchecker is installed and provide list of languages
    """
    try:
        import enchant

        if (directory):
            enchant.set_param("enchant.myspell.dictionary.path", directory)
        langs = enchant.list_languages()
        return sorted(langs)

    except:
        print "can not start spellchecker!!!"
        import traceback
        traceback.print_exc()
        return None
