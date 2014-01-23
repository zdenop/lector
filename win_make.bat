@ECHO OFF
SET pyinstaller=c:\Python27\Scripts\pyinstaller.exe

:Loop
IF "%1"=="clean" GOTO clean
IF "%1"=="build" GOTO build
IF "%1"=="exe" GOTO exe

:build
(
  echo Building Lector...
  CALL pylupdate4 lector.pro
  CALL lrelease lector.pro
  CALL pyrcc4 ui/resources.qrc -o lector/ui/resources_rc.py  
  CALL pyuic4 ui/ui_lector.ui -o lector/ui/ui_lector.py
  CALL pyuic4 ui/ui_settings.ui -o lector/ui/ui_settings.py
  CALL pyuic4 ui/ui_scanner.ui -o lector/ui/ui_scanner.py
  GOTO end
  REM EXIT /B 0
)

:clean
  rm -f lector/ui/ui_*.py lector/ui/resources*.py lector/ui/*.pyc
  rm -f lector/*.pyc lector/editor/*.pyc lector/utils/*.pyc ts/lector_*.qm
  GOTO end
  
:exe
  %pyinstaller% --onefile "e:\01_old_notebook\usr\projects\lector-ocr-code.devel\lector.pyw"
  GOTO end
 
:end
  echo Done!
REM DOC
REM http://www.robvanderwoude.com/parameters.php
REM http://ss64.com/nt/syntax-args.html
REM http://skypher.com/index.php/2010/08/17/batch-command-line-arguments/
