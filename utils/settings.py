from PyQt4.QtCore import QSettings, QVariant
from PyQt4.QtGui import QFont

def set(name, value):
    settings = QSettings("Davide Setti", "Lector")
    settings.setValue(name, QVariant(value))

def get(name):
    settings = QSettings("Davide Setti", "Lector")
    if name == 'scanner:height':
        return settings.value(name, QVariant(297)).toInt()[0]
    elif name == 'scanner:width':
        return settings.value(name, QVariant(210)).toInt()[0]
    elif name == 'scanner:resolution':
        return settings.value(name, QVariant(300)).toInt()[0]
    elif name == 'scanner:mode':
        return str(settings.value(name, QVariant("Color")).toString())
    elif name == 'scanner:device':
        return str(settings.value(name).toString())
    elif name == 'editor:font':
        return settings.value(name, QFont(QFont("Courier New", 10)))
    elif name == 'editor:clear':
        return str(settings.value(name, "true").toString()).lower() == "true"
    elif name == 'editor:spell':
        return str(settings.value(name, "true").toString()).lower() == "true"
    elif name == 'editor:whiteSpace':
        return str(settings.value(name, "true").toString()).lower() == "true"
    elif name == 'spellchecker:pwlLang':
        return str(settings.value(name, "true").toString()).lower() == "true"
    elif name == 'spellchecker:pwlDict':
        return str(settings.value(name, "my-dict.txt").toString())
    else:
        return str(settings.value(name).toString())

