# -*- mode: python -*-

import glob
import os.path
import sys

a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'lector.py'],
             pathex=['c:\\usr\\projects\\lector.devel'],
             #excludes=['Tkinter', 'wx', 'gtk', 'tcl', 'glib', 'PyQt4.QtWebKit', 'PyQt4.QtNetwork', 'PyQt4.QtSql']
             excludes=['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'gtk',
            'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs',
            'PyQt4.QtDesigner', 'PyQt4.QtNetwork', 'PyQt4.QtOpenGL',
            'PyQt4.QtScript', 'PyQt4.QtSql', 'PyQt4.QtTest',
            'PyQt4.QtWebKit', 'PyQt4.QtXml', 'PyQt4.phonon',
            'wx', 'tcl', 'Tkconstants', 'Tkinter'])
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

# not need dll
remove_dll_coll = []
remove_dll = ['tcl85.dll', 'tk85.dll']
for dll in remove_dll:
    remove_dll_coll.append((dll, '', ''))

coll = COLLECT( exe,
               a.binaries - remove_dll_coll + enchant_libs,
               #a.binaries + enchant_libs,
               enchant_eng,
               enchant_dicts,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=os.path.join('dist', 'Lector'))
app = BUNDLE(coll,
             name=os.path.join('dist', 'Lector.app'))
