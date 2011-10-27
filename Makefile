all: res translation

resources:
	pyrcc4 -o ui/resources_rc.py ui/resources.qrc
	pyuic4 -o ui/ui_lector.py ui/ui_lector.ui
	pyuic4 -o ui/ui_settings.py ui/ui_settings.ui
	pyuic4 -o ui/ui_scanner.py ui/ui_scanner.ui
	
res: resources

translation:
	lrelease lector.pro

up_translation:
	pylupdate4 lector.pro

clean:
	rm -f ui/ui_*.py ui/resources*.py ts/qt_it_IT.qm ts/lector_*.qm *.pyc
