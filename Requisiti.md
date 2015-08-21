# Generale #
In generale il software necessario comprende:
  * tesseract >= 2.00 con pacchetti per la lingua
  * python
  * pil
  * pyqt4
  * abiword (con plugin per leggere HTML)
  * pyqt4-dev-tools (serve solo per generare il codice dell'interfaccia, usando pyuic4)


# Ubuntu #
## Gutsy ##
```
apt-get install abiword abiword-plugins python-qt4 python-imaging pyqt4-dev-tools
```

Scaricare poi i pacchetti di tesseract (core + lingua) per Ubuntu Hardy da http://packages.ubuntu.com :

  * [tesseract core](http://packages.ubuntu.com/hardy/i386/tesseract-ocr/download)
  * [lingua italiana](http://packages.ubuntu.com/hardy/all/tesseract-ocr-ita/download)

e installarli con

```
dpkg -i tesseract*deb
```