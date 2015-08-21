#labels Phase-Requirements


# General Infos #

Requirements:
  * tesseract >= 2.04 (with language packages) with leptonica support
  * python
  * pil
  * pyqt4 >= 4.3
  * pil-sane (optional - if you want Linux scanning support)
  * sane-utils (optional - if you want Linux scanning support)
  * enchant (optional - if you want spellchecker support)

If using SVN sources also the following are needed:
  * pyqt4-dev-tools >= 4.3

If you are using win32 package on windows you just need [tesseract](http://tesseract-ocr.googlecode.com/files/tesseract-ocr-setup-3.01-1.exe) (python, QT4, enchant libs are bundled)

# INSTALLATION: users #

# Ubuntu #

```
sudo apt-get install python-qt4 python-imaging-sane sane-utils tesseract-ocr tesseract-ocr-eng
```

# INSTALLATION: developers #

# Ubuntu #

```
sudo apt-get install python-qt4 python-imaging-sane sane-utils libqt4-dev pyqt4-dev-tools tesseract-ocr tesseract-ocr-eng
```


# Debian #
## Etch - 4.0 ##

### requirements ###
for Debian there's a problem: the packages available on the official repositories are not up to date (the version is 1.02) as well as the qt4 libraries for python.
Before installing it's better to control if you have still these programs installed on your machine:

```
# dpkg -l | grep tesseract
# dpkg -l | grep qt4
# dpkg -l | grep python-imaging-sane
```

if the versions don't match the requirements above than procede with the steps here:

### tesseract-ocr ###
  * configure apt for using testing's repository
```
# vi /etc/apt/sources.list
    # Lenny
    deb http://ftp.it.debian.org/debian/ testing main contrib non-free
    deb http://security.debian.org/ testing/updates main contrib

# vi /etc/apt/apt.conf.d/20lenny
    APT::Default-Release "stable";
    APT::Cache-Limit 104857600;
```

the configuration file "20lenny" is worte in this way because:
  * 'APT::Default-Release "stable";': is used for choosing the stable as the default repository (in this way it doesn't upgrade to lenny).
  * 'APT::Cache-Limit 104857600;': it's needed because you'll have two repositories instead of one and so the database has to be bigger (may be 100M is too much but I think it won't be a problem if you have enogh space on your hard-disk).

  * installation of tesseract
```
# apt-get install -t lenny tesseract-ocr
```

you will be asked for a glibc upgrade and, of course, you we'll need to do it. After this is a good idea to reboot (so all the programs will use the new glibc).


### qt4 ###

you have just configured everything before so now it's simply so:
```
# apt-get install -t lenny pyqt4-dev-tools python-qt4 qt4-dev-tools libqt4-dev python-imaging-sane
```

Enjoy!