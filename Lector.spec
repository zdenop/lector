# -*- mode: python -*-

import glob
import os.path
import sys

a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'lector.pyw'],
            pathex=['c:\\usr\\projects\\lector.devel'],
            excludes=['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'gtk',
            'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs',
            'PyQt4.QtDesigner', 'PyQt4.QtNetwork', 'PyQt4.QtOpenGL',
            'PyQt4.QtSql', 'PyQt4.QtTest', 'PyQt4.QtScript',
            'PyQt4.QtWebKit', 'PyQt4.phonon',
            'wx', 'tcl', 'Tkconstants', 'Tkinter', '_tkinter'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
        a.scripts,
        exclude_binaries=1,
        name=os.path.join('build\\pyi.win32\\Lector', 'Lector.exe'),
        debug=False,
        strip=False,
        upx=True,
        console=False, icon='icons\L.ico')

# Enchant is not encluded ;-)
enchant_path = os.path.join(sys.prefix, 'Lib', 'site-packages', 'enchant')
enchant_eng = Tree(os.path.join(enchant_path, 'lib'), 'lib')
enchant_dicts = Tree(os.path.join(enchant_path, 'share'), 'share')
enchant_libs = []
for lib in glob.glob('%s\\*.dll' % enchant_path):
    enchant_libs.append((os.path.basename(lib), lib , 'BINARY'))

# not needed dll but it alse remove QT4.dll ;-)
remove_dll_coll = []
remove_dll = ['tcl85.dll', 'tk85.dll']
for dll in remove_dll:
    remove_dll_coll.append((dll, '', ''))

pyqt4_path = os.path.join(sys.prefix, 'Lib', 'site-packages', 'PyQt4')
add_dll_coll = []
add_dll = ['QtCore4.dll', 'QtGui4.dll', 'QtSvg4.dll', 'QtXml4.dll']
for a_dll in add_dll:
    add_dll_coll.append((a_dll, '%s\%s' % (pyqt4_path, a_dll) , 'BINARY'))

print remove_dll_coll

coll = COLLECT( exe,
            a.binaries - remove_dll_coll + enchant_libs + add_dll_coll,
            enchant_eng,
            enchant_dicts,
            a.zipfiles,
            a.datas,
            strip=False,
            upx=True,
            name=os.path.join('dist', 'Lector'))
hiddenimports = ['sip', 'PyQt4.QtCore', 'PyQt4.QtGui', 'PyQt4._qt']
app = BUNDLE(coll,
            name=os.path.join('dist', 'Lector.app'))
