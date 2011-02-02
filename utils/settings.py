from PyQt4.QtCore import QSettings, QVariant

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