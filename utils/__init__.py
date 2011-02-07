from PyQt4.QtGui import QImage
from PyQt4.QtCore import QByteArray
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
    invalid_path = error_message.split()[-1]
    path, invalid_fn = os.path.split(invalid_path)
    _, extension = os.path.splitext(invalid_fn)
    return path, extension


def get_tesseract_languages():
    if os.getenv('TESSDATA_PREFIX') is None:
        try:
            poTess = Popen(['tesseract', 'a', 'a', '-l', 'invalid'], -1,
                            stderr=PIPE)
        except OSError:
            return None
        lTess = poTess.stderr.readline()
        tessdata_path, langdata_ext = extract_tesseract_languages_path(lTess)
    else:
        tessdata_path = os.path.join(os.getenv('TESSDATA_PREFIX'), "tessdata")
        langdata_ext = '.unicharset'

    langdata = glob(tessdata_path + os.path.sep + '*' + langdata_ext)
    return [os.path.splitext(os.path.split(uc)[1])[0] for uc in langdata]