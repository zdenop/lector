all: ui translation res

ui:
	pyuic4 ui/ui_lector.ui > ui/ui_lector.py
	pyuic4 ui/ui_settings.ui > ui/ui_settings.py
	pyuic4 ui/ui_scanner.ui > ui/ui_scanner.py

resources:
	pyrcc4 -o ui/resources_rc.py ui/resources.qrc

res: resources

translation:
	lrelease lector.pro

up_translation:
	pylupdate4 lector.pro

clean:
	rm -f ui/ui_*.py ui/resources*.py ts/qt_it_IT.qm ts/lector_*.qm *.pyc
