from PyQt4.QtGui import QImage
from PyQt4.QtCore import QByteArray

def pilImage2Qt(im):
    ## TODO: check if it's necessary to convert to RGB (maybe only for grayscale images)
    s = im.convert("RGB").tostring("jpeg","RGB")

    qtimage = QImage()
    qtimage.loadFromData(QByteArray(s))
    return qtimage

    #self.ocrImage = ImageQt.ImageQt(self.im.convert("RGB"))

