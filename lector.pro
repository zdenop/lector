#TEMPLATE = app
#TARGET = 
#DEPENDPATH += .
#INCLUDEPATH += .

# Input
SOURCES         += lector.pyw \
                   ocrarea.py ocrscene.py ocrwidget.py \
                   scannerselect.py scannerthread.py settingsdialog.py \
                   editor/textwidget.py editor/spellchecker.py \
                   utils/settings.py

FORMS           += ui/ui_lector.ui \
                   ui/ui_settings.ui \
                   ui/ui_scanner.ui

TRANSLATIONS    =  ts/lector_en_GB.ts \
                   ts/lector_it_IT.ts \
                   ts/lector_de_DE.ts \
                   ts/lector_sk_SK.ts

RESOURCES       =  ui/resources.qrc
