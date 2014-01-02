#!/usr/bin/env python
"""
Lector - A graphical ocr solution for GNU/Linux based on Python, Qt4 and
Tesseract OCR.
Copyright (c) 2011-2013 Davide Setti, Zdenko Podobny

This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 2 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

#from distutils.command.install_scripts import install_scripts
from distutils.core import setup

setup(name = 'lector',
    description = 'Graphical OCR solution',
    version = '0.3.0',
    author = 'Davide Setti',
    url = 'http://code.google.com/p/lector/',
    package_dir = {'lector': './'},
    packages = ['editor', 'icons', 'ui', 'utils', 'ts'],
    data_files = ['AUTHORS', 'CREDITS', 'ChangeLog', 'LICENSE', 
        'README'],
    scripts = ['./lector.pyw', 'ocrarea.py', 'ocrscene.py', 
        'ocrwidget.py', 'scannerselect.py', 
        'scannerthread.py', 'settingsdialog.py', 'Makefile'],
    license = 'GPLv2',
    long_description = '''A graphical ocr solution for GNU/Linux based 
        on Python, Qt4 and tessaract OCR''',

    classifiers=[
        'Development Status :: 0.3.0',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Education',
        'Natural Language :: German',
        'Natural Language :: Italian',
        'Natural Language :: Slovak',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Multimedia',
        'Topic :: Multimedia :: Graphics'
        ],
 
    )

