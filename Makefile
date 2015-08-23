all: translation res

resources:
	pyrcc5 ui/resources.qrc -o lector/resources_rc.py
	pyuic5 ui/ui_lector.ui -o lector/ui/ui_lector.py
	pyuic5 ui/ui_settings.ui -o lector/ui/ui_settings.py
	pyuic5 ui/ui_scanner.ui -o lector/ui/ui_scanner.py
	
res: resources

translation:
	lrelease lector.pro

up_translation:
	pylupdate4 lector.pro

clean:
	rm -f lector/ui/ui_*.py lector/resources*.py lector/ui/*.pyc
	rm -f lector/*.pyc lector/editor/*.pyc lector/utils/*.pyc ts/lector_*.qm 

install: all
	python setup.py build
	sudo python setup.py install --record lector_files.txt
